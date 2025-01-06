"""Service for executing jupyter notebooks interactively
Partially referenced the implementation of
https://github.com/modelscope/agentscope/blob/main/src/agentscope/service/execute_code/exec_notebook.py
"""
import base64
import asyncio
from loguru import logger

try:
    import nbclient
    import nbformat
except ImportError:
    nbclient = None
    nbformat = None


import os, asyncio, re
from typing import List, Optional
from loguru import logger
from ..base_configs.env_config import KB_ROOT_PATH
from .basebox import BaseBox, CodeBoxResponse, CodeBoxStatus



class NoteBookExecutor:
    """
    Class for executing jupyter notebooks block interactively.
    To use the service function, you should first init the class, then call the
    run_code_on_notebook function.

    Example:

        ```ipython
        from agentscope.service.service_toolkit import *
        from agentscope.service.execute_code.exec_notebook import *
        nbe = NoteBookExecutor()
        code = "print('helloworld')"
        # calling directly
        nbe.run_code_on_notebook(code)

        >>> Executing function run_code_on_notebook with arguments:
        >>>     code: print('helloworld')
        >>> END

        # calling with service toolkit
        service_toolkit = ServiceToolkit()
        service_toolkit.add(nbe.run_code_on_notebook)
        input_obs = [{"name": "run_code_on_notebook", "arguments":{"code": code}}]
        res_of_string_input = service_toolkit.parse_and_call_func(input_obs)

        "1. Execute function run_code_on_notebook\n   [ARGUMENTS]:\n       code: print('helloworld')\n   [STATUS]: SUCCESS\n   [RESULT]: ['helloworld\\n']\n"

        ```
    """  # noqa

    def __init__(
        self,
        timeout: int = 300,
        work_path: str = KB_ROOT_PATH,
    ) -> None:
        """
        The construct function of the NoteBookExecutor.
        Args:
            timeout (Optional`int`):
                The timeout for each cell execution.
                Default to 300.
        """

        if nbclient is None or nbformat is None:
            raise ImportError(
                "The package nbclient or nbformat is not found. Please "
                "install it by `pip install notebook nbclient nbformat`",
            )

        self.nb = nbformat.v4.new_notebook()
        self.nb_client = nbclient.NotebookClient(nb=self.nb)
        self.work_path = work_path
        self.ori_path = os.getcwd()
        self.timeout = timeout

        asyncio.run(self._start_client())

    def _output_parser(self, output: dict) -> str:
        """Parse the output of the notebook cell and return str"""
        if output["output_type"] == "stream":
            return output["text"]
        elif output["output_type"] == "execute_result":
            return output["data"]["text/plain"]
        elif output["output_type"] == "display_data":
            if "image/png" in output["data"]:
                file_path = self._save_image(output["data"]["image/png"])
                return f"Displayed image saved to {file_path}"
            else:
                return "Unsupported display type"
        elif output["output_type"] == "error":
            return output["traceback"]
        else:
            logger.info(f"Unsupported output encountered: {output}")
            return "Unsupported output encountered"

    async def _start_client(self) -> None:
        """start notebook client"""
        if self.nb_client.kc is None or not await self.nb_client.kc.is_alive():
            os.chdir(self.work_path)
            self.nb_client.create_kernel_manager()
            self.nb_client.start_new_kernel()
            self.nb_client.start_new_kernel_client()
            os.chdir(self.ori_path)

    async def _kill_client(self) -> None:
        """kill notebook client"""
        if (
            self.nb_client.km is not None
            and await self.nb_client.km.is_alive()
        ):
            await self.nb_client.km.shutdown_kernel(now=True)
            await self.nb_client.km.cleanup_resources()

        self.nb_client.kc.stop_channels()
        self.nb_client.kc = None
        self.nb_client.km = None

    async def _restart_client(self) -> None:
        """Restart the notebook client"""
        await self._kill_client()
        self.nb_client = nbclient.NotebookClient(self.nb, timeout=self.timeout)
        await self._start_client()

    async def _run_cell(self, cell_index: int):
        """Run a cell in the notebook by its index"""
        try:
            self.nb_client.execute_cell(self.nb.cells[cell_index], cell_index)
            return self.nb.cells[cell_index].outputs
            return [self._output_parser(output) for output in self.nb.cells[cell_index].outputs]
        except nbclient.exceptions.DeadKernelError:
            await self.reset_notebook()
            return "DeadKernelError when executing cell, reset kernel"
        except nbclient.exceptions.CellTimeoutError:
            assert self.nb_client.km is not None
            await self.nb_client.km.interrupt_kernel()
            return (
                    "CellTimeoutError when executing cell"
                    ", code execution timeout"
                )
        except Exception as e:
            return str(e)

    @property
    def cells_length(self) -> int:
        """return cell length"""
        return len(self.nb.cells)

    async def async_run_code_on_notebook(self, code: str):
        """
        Run the code on interactive notebook
        """
        self.nb.cells.append(nbformat.v4.new_code_cell(code))
        cell_index = self.cells_length - 1
        return await self._run_cell(cell_index)

    def run_code_on_notebook(self, code: str):
        """
        Run the code on interactive jupyter notebook.

        Args:
            code (`str`):
                The Python code to be executed in the interactive notebook.

        Returns:
            `ServiceResponse`: whether the code execution was successful,
            and the output of the code execution.
        """
        return asyncio.run(self.async_run_code_on_notebook(code))

    def reset_notebook(self) -> str:
        """
        Reset the notebook
        """
        asyncio.run(self._restart_client())
        return "Reset notebook"
    




class NBClientBox(BaseBox):

    enter_status: bool = False

    def __init__(
            self, 
            do_code_exe: bool = False,
            work_path: str = KB_ROOT_PATH,
    ):
        self.nbe = NoteBookExecutor(work_path=work_path)
        self.do_code_exe = do_code_exe

    def decode_code_from_text(self, text: str) -> str:
        pattern = r'```.*?```'
        code_blocks = re.findall(pattern, text, re.DOTALL)
        code_text: str = "\n".join([block.strip('`') for block in code_blocks])
        code_text = code_text[6:] if code_text.startswith("python") else code_text
        code_text = code_text.replace("python\n", "").replace("code", "")
        return code_text
    
    def run(
            self, code_text: Optional[str] = None,
            file_path: Optional[os.PathLike] = None,
            retry = 3,
    ) -> CodeBoxResponse:
        if not code_text and not file_path:
            return CodeBoxResponse(
                code_exe_response="Code or file_path must be specifieds!",
                code_text=code_text,
                code_exe_type="text",
                code_exe_status=502,
                do_code_exe=self.do_code_exe,
            )
        
        if code_text and file_path:
            return CodeBoxResponse(
                code_exe_response="Can only specify code or the file to read_from!",
                code_text=code_text,
                code_exe_type="text",
                code_exe_status=502,
                do_code_exe=self.do_code_exe,
            )
        
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                code_text = f.read()


        def _output_parser(output: dict) -> str:
            """Parse the output of the notebook cell and return str"""
            if output["output_type"] == "stream":
                return CodeBoxResponse(
                        code_exe_type="text",
                        code_text=code_text,
                        code_exe_response=output["text"] or "Code run successfully (no output)",
                        code_exe_status=200,
                        do_code_exe=self.do_code_exe
                    )
            elif output["output_type"] == "execute_result":
                return CodeBoxResponse(
                        code_exe_type="text",
                        code_text=code_text,
                        code_exe_response=output["data"]["text/plain"] or "Code run successfully (no output)",
                        code_exe_status=200,
                        do_code_exe=self.do_code_exe
                    )
            elif output["output_type"] == "display_data":
                if "image/png" in output["data"]:
                    return CodeBoxResponse(
                        code_exe_type="image/png",
                        code_text=code_text,
                        code_exe_response=output["data"]["image/png"],
                        code_exe_status=200,
                        do_code_exe=self.do_code_exe
                    )
                else:
                    return CodeBoxResponse(
                            code_exe_type="error",
                            code_text=code_text,
                            code_exe_response="Unsupported display type",
                            code_exe_status=420,
                            do_code_exe=self.do_code_exe
                        )
            elif output["output_type"] == "error":
                return CodeBoxResponse(
                        code_exe_type="error",
                        code_text=code_text,
                        code_exe_response="error",
                        code_exe_status=500,
                        do_code_exe=self.do_code_exe
                    )
            else:
                return CodeBoxResponse(
                        code_exe_type="error",
                        code_text=code_text,
                        code_exe_response=f"Unsupported output encountered: {output}",
                        code_exe_status=420,
                        do_code_exe=self.do_code_exe
                    )
            
        contents = self.nbe.run_code_on_notebook(code_text)
        content = contents[0]
        return _output_parser(content)
    
    def restart(self, ) -> CodeBoxStatus:
        return CodeBoxStatus(status="restared")
    
    def stop(self, ) -> CodeBoxStatus:
        pass
    
    def __del__(self):
        self.stop()