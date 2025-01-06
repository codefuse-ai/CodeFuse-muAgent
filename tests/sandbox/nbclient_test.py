# # -*- coding: utf-8 -*-
# # pylint: disable=C0301
# """Service for executing jupyter notebooks interactively
# Partially referenced the implementation of
# https://github.com/geekan/MetaGPT/blob/main/metagpt/actions/di/execute_nb_code.py
# """
# import base64
# import asyncio
# from loguru import logger

# try:
#     import nbclient
#     import nbformat
# except ImportError:
#     nbclient = None
#     nbformat = None


# class NoteBookExecutor:
#     """
#     Class for executing jupyter notebooks block interactively.
#     To use the service function, you should first init the class, then call the
#     run_code_on_notebook function.

#     Example:

#         ```ipython
#         from agentscope.service.service_toolkit import *
#         from agentscope.service.execute_code.exec_notebook import *
#         nbe = NoteBookExecutor()
#         code = "print('helloworld')"
#         # calling directly
#         nbe.run_code_on_notebook(code)

#         >>> Executing function run_code_on_notebook with arguments:
#         >>>     code: print('helloworld')
#         >>> END

#         # calling with service toolkit
#         service_toolkit = ServiceToolkit()
#         service_toolkit.add(nbe.run_code_on_notebook)
#         input_obs = [{"name": "run_code_on_notebook", "arguments":{"code": code}}]
#         res_of_string_input = service_toolkit.parse_and_call_func(input_obs)

#         "1. Execute function run_code_on_notebook\n   [ARGUMENTS]:\n       code: print('helloworld')\n   [STATUS]: SUCCESS\n   [RESULT]: ['helloworld\\n']\n"

#         ```
#     """  # noqa

#     def __init__(
#         self,
#         timeout: int = 300,
#     ) -> None:
#         """
#         The construct function of the NoteBookExecutor.
#         Args:
#             timeout (Optional`int`):
#                 The timeout for each cell execution.
#                 Default to 300.
#         """

#         if nbclient is None or nbformat is None:
#             raise ImportError(
#                 "The package nbclient or nbformat is not found. Please "
#                 "install it by `pip install notebook nbclient nbformat`",
#             )

#         self.nb = nbformat.v4.new_notebook()
#         self.nb_client = nbclient.NotebookClient(nb=self.nb)
#         self.timeout = timeout

#         asyncio.run(self._start_client())

#     def _output_parser(self, output: dict) -> str:
#         """Parse the output of the notebook cell and return str"""
#         if output["output_type"] == "stream":
#             return output["text"]
#         elif output["output_type"] == "execute_result":
#             return output["data"]["text/plain"]
#         elif output["output_type"] == "display_data":
#             if "image/png" in output["data"]:
#                 file_path = self._save_image(output["data"]["image/png"])
#                 return f"Displayed image saved to {file_path}"
#             else:
#                 return "Unsupported display type"
#         elif output["output_type"] == "error":
#             return output["traceback"]
#         else:
#             logger.info(f"Unsupported output encountered: {output}")
#             return "Unsupported output encountered"

#     async def _start_client(self) -> None:
#         """start notebook client"""
#         if self.nb_client.kc is None or not await self.nb_client.kc.is_alive():
#             self.nb_client.create_kernel_manager()
#             self.nb_client.start_new_kernel()
#             self.nb_client.start_new_kernel_client()

#     async def _kill_client(self) -> None:
#         """kill notebook client"""
#         if (
#             self.nb_client.km is not None
#             and await self.nb_client.km.is_alive()
#         ):
#             await self.nb_client.km.shutdown_kernel(now=True)
#             await self.nb_client.km.cleanup_resources()

#         self.nb_client.kc.stop_channels()
#         self.nb_client.kc = None
#         self.nb_client.km = None

#     async def _restart_client(self) -> None:
#         """Restart the notebook client"""
#         await self._kill_client()
#         self.nb_client = nbclient.NotebookClient(self.nb, timeout=self.timeout)
#         await self._start_client()

#     async def _run_cell(self, cell_index: int):
#         """Run a cell in the notebook by its index"""
#         try:
#             self.nb_client.execute_cell(self.nb.cells[cell_index], cell_index)
#             return [self._output_parser(output) for output in self.nb.cells[cell_index].outputs]
#         except nbclient.exceptions.DeadKernelError:
#             await self.reset_notebook()
#             return "DeadKernelError when executing cell, reset kernel"
#         except nbclient.exceptions.CellTimeoutError:
#             assert self.nb_client.km is not None
#             await self.nb_client.km.interrupt_kernel()
#             return (
#                     "CellTimeoutError when executing cell"
#                     ", code execution timeout"
#                 )
#         except Exception as e:
#             return str(e)

#     @property
#     def cells_length(self) -> int:
#         """return cell length"""
#         return len(self.nb.cells)

#     async def async_run_code_on_notebook(self, code: str):
#         """
#         Run the code on interactive notebook
#         """
#         self.nb.cells.append(nbformat.v4.new_code_cell(code))
#         cell_index = self.cells_length - 1
#         return await self._run_cell(cell_index)

#     def run_code_on_notebook(self, code: str):
#         """
#         Run the code on interactive jupyter notebook.

#         Args:
#             code (`str`):
#                 The Python code to be executed in the interactive notebook.

#         Returns:
#             `ServiceResponse`: whether the code execution was successful,
#             and the output of the code execution.
#         """
#         return asyncio.run(self.async_run_code_on_notebook(code))

#     def reset_notebook(self) -> str:
#         """
#         Reset the notebook
#         """
#         asyncio.run(self._restart_client())
#         return "Reset notebook"
    

import os
from loguru import logger

try:
    import os, sys
    src_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.append(src_dir)
    import test_config
except Exception as e:
    # set your config
    logger.error(f"{e}")

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(src_dir)


from muagent.sandbox import NBClientBox, NoteBookExecutor

nbe = NoteBookExecutor()
code = f"""
x = 1
y = 1
z = x+y
print(z)
"""
print(nbe.run_code_on_notebook(code))


code = f"""z
"""
print(nbe.run_code_on_notebook(code))


codebox = NBClientBox()

reuslt = codebox.chat("```import os\nos.getcwd()```", do_code_exe=True)
print(reuslt)

reuslt = codebox.chat("```print('hello world!')```", do_code_exe=True)
print(reuslt)

with NBClientBox(do_code_exe=True) as codebox:
    result = codebox.run("'hello world!'")
    print(result)