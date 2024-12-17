import ast
import os
import libcst as cst
import libcst.matchers as m
from libcst.display import dump
from loguru import logger
class GlobalVariableVisitor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self):
        self.global_assigns = []

    def leave_Module(self, original_node: cst.Module) -> list:
        assigns = []
        for stmt in original_node.body:
            if m.matches(stmt, m.SimpleStatementLine()) and m.matches(
                stmt.body[0], m.Assign()
            ):
                start_pos = self.get_metadata(cst.metadata.PositionProvider, stmt).start
                end_pos = self.get_metadata(cst.metadata.PositionProvider, stmt).end
                assigns.append([stmt, start_pos, end_pos])
        self.global_assigns.extend(assigns)



def parse_global_var_from_code(file_content: str) -> dict[str, dict]:
    """Parse global variables."""
    try:
        tree = cst.parse_module(file_content)
    except:
        return file_content

    wrapper = cst.metadata.MetadataWrapper(tree)
    visitor = GlobalVariableVisitor()
    wrapper.visit(visitor)

    global_assigns = {}
    for assign_stmt, start_pos, end_pos in visitor.global_assigns:
        for t in assign_stmt.body:
            try:
                targets = [t.targets[0].target.value]
            except:
                try:
                    targets = t.targets[0].target.elements
                    targets = [x.value.value for x in targets]
                except:
                    targets = []
            for target_var in targets:
                global_assigns[target_var] = {
                    "start_line": start_pos.line,
                    "end_line": end_pos.line,
                }
    return global_assigns

def parse_python_file(file_path, file_content=None):
    """解析一个Python文件，提取类和函数定义以及它们的行号。
    :param file_path: Python文件的路径。
    :return: 类名、函数名以及文件内容
    """
    if file_content is None:
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                parsed_data = ast.parse(file_content)
        except Exception as e:  # 捕获所有类型的异常
            print(f"文件 {file_path} 解析错误: {e}")
            return [], [], ""
    else:
        try:
            parsed_data = ast.parse(file_content)
        except Exception as e:  # 捕获所有类型的异常
            print(f"文件 {file_path} 解析错误: {e}")
            return [], [], ""

    class_name_list = []
    func_name_dict = {}
    import_pac_name_list = []
    global_var = parse_global_var_from_code(file_content)
    for node in ast.walk(parsed_data):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_name_list.append(class_name)
            methods = []
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    func_name = f"{class_name}.{n.name}"
                    methods.append(func_name)
                    if class_name not in func_name_dict:
                        func_name_dict[class_name] = []
                    func_name_dict[class_name].append(func_name)
        elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
            func_name = node.name
            if func_name not in func_name_dict:
                func_name_dict[func_name] = []
            func_name_dict[func_name].append(func_name)
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            for alias in node.names:
                import_pac_name_list.append(alias.name)

    fp_last = file_path.split(os.path.sep)[-1]
    pac_name = f"{file_path}#{fp_last}"

    res = {
        'pac_name': pac_name,
        'class_name_list': class_name_list,
        'func_name_dict': func_name_dict,
        'import_pac_name_list': import_pac_name_list
    }
    return res

class PythonStaticAnalysis:
    def __init__(self):
        pass
    def analyze(self, python_code_dict):
        '''
        parse python code and extract entity
        '''
        res = {}
        for fp, python_code in python_code_dict.items():
            tmp = parse_python_file(fp, python_code)
            res[python_code] = tmp
        return res
    
if __name__ == '__main__':
    python_code_dict = {
        'test': '''import unittest

class UtilsTest(unittest.TestCase):
    def test_remove_char(self):
        input_str = "hello"
        ch = 'l'
        expected = "heo"
        res = Utils.remove(input_str, ch)
        self.assertEqual(res, expected)

if __name__ == "__main__":
    unittest.main()
'''
    }

    psa = PythonStaticAnalysis()
    res = psa.analyze(python_code_dict)
    logger.info(res)