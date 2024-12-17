# encoding: utf-8
'''
@author: 温进
@file: __init__.py.py
@time: 2023/11/21 下午4:24
@desc:
'''

from .java_static_analysis import JavaStaticAnalysis
from .python_static_analysis import PythonStaticAnalysis

__all__ = [
    'JavaStaticAnalysis','PythonStaticAnalysis'
    ]