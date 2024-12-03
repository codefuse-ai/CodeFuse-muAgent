analyze_project_tree_prompt_add_prompt = """
Input:
[项目目录架构]
{dictory_structure}
[用户issue]
{user_issue}
Output:

"""

analyze_files_project_tree_prompt = """
你是一名代码架构专家，根据用户提供的issue，判断项目中哪个文件可能可以回答问题。

请按照以下JSON格式进行响应：
{
    "files": {
        "thoughts": "用中文说明为何选择这些文件，如果没有确定的文件路径则留空。",
        "file_path": ["如果确定需要修改的文件路径，一定要包含项目目录架构最外层的完整路径，请基于项目目录架构提供，最多5个"]
    }
}
##NOTE：
要是路径一定要跟着项目目录架构，否则会出现问题。
django/
    Gruntfile.js
    scripts/
        manage_translations.py
        rpm-install.sh
    django/
        templatetags/
            l10n.py
比如想要找l10n.py这个文件一定要按照这样输出：'django/django/templatetags/l10n.py'

规则：
- file_path 最多五个元素。
- 不要输出其他信息，避免使用引号（例如`, \", \'等）。
- 确保输出可以被Python的 `json.loads` 解析。
- 不要使用markdown格式，例如```json或```，只需以相应的字符串格式输出。
Input:
[项目目录架构]
django/
    Gruntfile.js
    .git-blame-ignore-revs
    INSTALL
    LICENSE
    CONTRIBUTING.rst
    AUTHORS
    .pre-commit-config.yaml
    pyproject.toml
    .eslintrc
    MANIFEST.in
    .readthedocs.yml
    .editorconfig
    LICENSE.python
    setup.py
    .gitignore
    package.json
    tox.ini
    .gitattributes
    setup.cfg
    .eslintignore
    README.rst
    scripts/
        manage_translations.py
        rpm-install.sh
    django/
        shortcuts.py
        __init__.py
        __main__.py
        templatetags/
            l10n.py
            tz.py
            cache.py
            __init__.py
            static.py
            i18n.py
        template/
            library.py
            __init__.py
            response.py
            smartif.py
            context_processors.py
            defaultfilters.py
            engine.py
            context.py
            utils.py
            loader.py
            loader_tags.py
            exceptions.py
            autoreload.py
            base.py
            defaulttags.py
        

[用户issue]
New template filter `escapeseq`
Description
	
Following #34574, and after some conversations within the security team, it seems appropriate to provide a new template filter escapeseq which would be to escape what safeseq is to safe. An example of usage would be:
{{ some_list|escapeseq|join:"," }}
where each item of some_list is escaped before applying the join operation. This usage makes sense in a context where autoescape is off.

Output:
{
    "files": {
        "thoughts": "新的模板过滤器escapeseq会涉及到过滤器的具体实现文件。根据Django项目结构，这些过滤器通常定义在defaultfilters.py文件中。",
        "file_path": ["django/django/template/defaultfilters.py"]
    }
}
"""