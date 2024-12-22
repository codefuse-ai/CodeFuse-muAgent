import os
import git
from dotenv import load_dotenv
import urllib.parse



def get_directory_structure(directory_path:str, notallow:set=None):
    """
    获取指定目录下的文件结构并返回为字符串格式。

    :param directory_path: str, 目录路径
    :param notallow: set, 不允许包含的文件或目录集合，默认值为None
    :return: str, 文件结构
    """
    structure = []
    notallow_dict = {'.git', '__pycache__', '.idea','.github','.tx'}

    # 如果 notallow 参数不为空，将其合并到 notallow_dict 中
    if notallow:
        notallow_dict.update(notallow)
    for root, dirs, files in os.walk(directory_path):
        # 过滤掉不需要的目录
        dirs[:] = [d for d in dirs if d not in notallow_dict]

        level = root.replace(directory_path, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            structure.append(f"{sub_indent}{file}")

    return "\n".join(structure)

# 开始检查 code_path 是否是 Java 项目
def check_java_project(code_path):
    # 检查是否存在 pom.xml 文件
    if not os.path.exists(os.path.join(code_path, "pom.xml")):
        # 如果没有 pom.xml 文件，检查是否有 .java 文件
        has_java_file = False
        for root, dirs, files in os.walk(code_path):
            if any(file.endswith(".java") for file in files):
                has_java_file = True
                break
        # 如果既没有 pom.xml 也没有 .java 文件，抛出异常
        if not has_java_file:
            raise Exception(f"code_path {code_path} is not a Java project")
    print(f"code_path {code_path} is a Java project")
    
def clone_repo_with_token(repo_url, clone_to):
    """
    克隆一个需要认证的GitHub仓库。

    参数:
    repo_url (str): 原始仓库的URL。
    clone_to (str): 克隆到的本地目录。

    返回:
    str: 成功时返回克隆到的本地目录（包含子目录），不成功时返回空字符串。
    """
    try:
        if not os.path.exists(clone_to):
            os.makedirs(clone_to)
        load_dotenv()
        # 从环境变量中获取令牌
        token = os.getenv('github_token')
        if not token:
            raise ValueError("GitHub token not found in environment variables")

        # 提取仓库的域名和路径
        if repo_url.startswith("https://"):
            repo_url = repo_url.replace("https://", f"https://{token}@")
        elif repo_url.startswith("http://"):
            repo_url = repo_url.replace("http://", f"http://{token}@")

        # 从URL中提取仓库名称
        repo_name = urllib.parse.urlparse(repo_url).path.split('/')[-1]

        # 在clone_to目录下创建新的目录
        cloned_path = os.path.join(clone_to, repo_name)
        if os.path.exists(cloned_path):
            return cloned_path
        # 克隆仓库
        repo = git.Repo.clone_from(repo_url, cloned_path)
        
        print(f"Repository cloned to {cloned_path}")
        return cloned_path
    except Exception as e:
        print(f"Failed to clone repository: {e}")
        return ''