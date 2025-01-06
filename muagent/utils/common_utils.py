import time, hashlib, json, os
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
from typing import *
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
import json
import signal
import contextlib
import sys
import socket


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def getCurrentDatetime(dateformat=DATE_FORMAT):
    return datetime.now().strftime(dateformat)

def getCurrentTimestap():
    return int(datetime.now().timestamp())

def addMinutesToTime(input_time: str, n: int = 5, dateformat=DATE_FORMAT):
    dt = datetime.strptime(input_time, dateformat)

    # 前后加N分钟
    new_time_before = dt - timedelta(minutes=n)
    new_time_after = dt + timedelta(minutes=n)
    return new_time_before.strftime(dateformat), new_time_after.strftime(dateformat)

def addMinutesToTimestamp(input_time: str, n: int = 5, dateformat=DATE_FORMAT):
    dt = datetime.strptime(input_time, dateformat)

    # 前后加N分钟
    new_time_before = dt - timedelta(minutes=n)
    new_time_after = dt + timedelta(minutes=n)
    return new_time_before.timestamp(), new_time_after.timestamp()

def timestampToDateformat(ts, interval=1000, dateformat=DATE_FORMAT):
    '''将标准时间戳转换标准指定时间格式'''
    return datetime.fromtimestamp(ts/interval).strftime(dateformat)


def dateformatToTimestamp(dt, interval=1000, dateformat=DATE_FORMAT):
    '''将标准时间格式转换未标准时间戳'''
    return int(datetime.strptime(dt, dateformat).timestamp()*interval)


def func_timer(function):
    '''
    用装饰器实现函数计时
    :param function: 需要计时的函数
    :return: None
    '''
    @wraps(function)
    def function_timer(*args, **kwargs):
        # logger.info('[Function: {name} start...]'.format(name=function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        logger.info('[Function: {name} finished, spent time: {time:.3f}s]'.format(
            name=function.__name__,
            time=t1 - t0))
        return result
    return function_timer


def custom_serializer(obj):
    try:
        return str(obj)
    except TypeError:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def read_jsonl_file(filename):
    data = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def save_to_jsonl_file(data, filename):
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name): os.makedirs(dir_name)

    with open(filename, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def read_json_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
    
    
def save_to_json_file(data, filename):
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name): os.makedirs(dir_name)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=custom_serializer)


def file_normalize(file: Union[str, Path, bytes], filename=None):
    # logger.debug(f"{file}")
    if isinstance(file, bytes): # raw bytes
        file = BytesIO(file)
    elif hasattr(file, "read"): # a file io like object
        filename = filename or file.name
    else: # a local path
        file = Path(file).absolute().open("rb")
        # logger.debug(file)
        filename = filename or file.name
    return file, filename


def get_uploadfile(file: Union[str, Path, bytes], filename=None) -> UploadFile:
    temp_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
    temp_file.write(file.read())
    temp_file.seek(0)
    return UploadFile(file=temp_file, filename=filename)


def string_to_long_sha256(s: str) -> int:
    # 使用 SHA-256 哈希函数
    hash_object = hashlib.sha256(s.encode())
    # 转换为16进制然后转换为整数
    return int(hash_object.hexdigest(), 16)


def double_hashing(s: str, modulus: int = 10e12) -> int:
    hash1 = string_to_long_sha256(s)
    hash2 = string_to_long_sha256(s[::-1])  # 用字符串的反序进行第二次hash
    return int((hash1 + hash2) % modulus)


def _convert_to_str(content: Any) -> str:
    """Convert the content to string.

    The implementation of this _convert_to_str are borrowed from
    https://github.com/modelscope/agentscope/blob/main/src/agentscope/utils/common.py

    Note:
        For prompt engineering, simply calling `str(content)` or
        `json.dumps(content)` is not enough.

        - For `str(content)`, if `content` is a dictionary, it will turn double
        quotes to single quotes. When this string is fed into prompt, the LLMs
        may learn to use single quotes instead of double quotes (which
        cannot be loaded by `json.loads` API).

        - For `json.dumps(content)`, if `content` is a string, it will add
        double quotes to the string. LLMs may learn to use double quotes to
        wrap strings, which leads to the same issue as `str(content)`.

        To avoid these issues, we use this function to safely convert the
        content to a string used in prompt.

    Args:
        content (`Any`):
            The content to be converted.

    Returns:
        `str`: The converted string.
    """

    if isinstance(content, str):
        return content
    elif isinstance(content, (dict, list, int, float, bool, tuple)):
        return json.dumps(content, ensure_ascii=False)
    else:
        return str(content)


@contextlib.contextmanager
def timer(seconds: Optional[Union[int, float]] = None) -> Generator:
    """
    A context manager that limits the execution time of a code block to a
    given number of seconds.
    The implementation of this contextmanager are borrowed from
    https://github.com/openai/human-eval/blob/master/human_eval/execution.py

    Note:
        This function only works in Unix and MainThread,
        since `signal.setitimer` is only available in Unix.

    """
    if (
        seconds is None
        or sys.platform == "win32"
        or threading.currentThread().name  # pylint: disable=W4902
        != "MainThread"
    ):
        yield
        return

    def signal_handler(*args: Any, **kwargs: Any) -> None:
        raise TimeoutError("timed out")

    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)

    try:
        # Enter the context and execute the code block.
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


class ImportErrorReporter:
    """Used as a placeholder for missing packages.
    When called, an ImportError will be raised, prompting the user to install
    the specified extras requirement.
    The implementation of this ImportErrorReporter are borrowed from
    https://github.com/modelscope/agentscope/src/agentscope/utils/common.py
    """

    def __init__(self, error: ImportError, extras_require: str = None) -> None:
        """Init the ImportErrorReporter.

        Args:
            error (`ImportError`): the original ImportError.
            extras_require (`str`): the extras requirement.
        """
        self.error = error
        self.extras_require = extras_require

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self._raise_import_error()

    def __getattr__(self, name: str) -> Any:
        return self._raise_import_error()

    def __getitem__(self, __key: Any) -> Any:
        return self._raise_import_error()

    def _raise_import_error(self) -> Any:
        """Raise the ImportError"""
        err_msg = f"ImportError occorred: [{self.error.msg}]."
        if self.extras_require is not None:
            err_msg += (
                f" Please install [{self.extras_require}] version"
                " of agentscope."
            )
        raise ImportError(err_msg)
    

def _find_available_port() -> int:
    """
    Get an unoccupied socket port number.
    The implementation of this _find_available_port are borrowed from
    https://github.com/modelscope/agentscope/src/agentscope/utils/common.py
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _check_port(port: Optional[int] = None) -> int:
    """Check if the port is available.
    The implementation of this _check_port are borrowed from
    https://github.com/modelscope/agentscope/src/agentscope/utils/common.py

    Args:
        port (`int`):
            the port number being checked.

    Returns:
        `int`: the port number that passed the check. If the port is found
        to be occupied, an available port number will be automatically
        returned.
    """
    if port is None:
        new_port = _find_available_port()
        return new_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            if s.connect_ex(("localhost", port)) == 0:
                raise RuntimeError("Port is occupied.")
        except Exception:
            new_port = _find_available_port()
            return new_port
    return port