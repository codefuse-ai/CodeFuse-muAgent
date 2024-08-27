1. nebula
简单修改muagent\codechat\code_search\code_search.py的search_by_cypher函数和muagent\codechat\code_search\cypher_generator.py的get_cypher函数
然后Prompt中有了用户上传的代码信息，模型能够根据信息给出回复
使用tag交互是可以的，不过用cypher代码交互时会有些问题：
项目中使用图数据库信息的方式，是将代码仓库的edge和node都存入数据库，提取出来，然后填入muagent\codechat\code_search\cypher_generator.py的schema模板，但我看项目中并没有这个传参的过程。于是我修改了schema
即muagent\codechat\code_search\code_search.py的search_by_cypher函数和muagent\codechat\code_search\cypher_generator.py的get_cypher函数
让他能看到图数据库信息。然后是可以生成cypher查询语句的，但qwen2 7b生成的查询语句存在问题，导致查询结果为空
因为数据库查询结果是valueWrapper组成的列表，我不知道怎么处理。我就直接把他转换为字符串，替代原有的schema，所以提供给大模型的信息可能不是很规范
我不太清楚是不是代码执行过程中遗漏了某个步骤，如果仓库本身缺少图数据库传参这块的代码，后面我就补充完善下这里，后面一起提交pr上去

2. ollama
start.py报错 安装 notebook 失败（不过容器正常启动，不知道是否会有影响）

3. guidance
outline不支持ollama，于是选用guidance
对包的版本进行了调整（pydantic 1.10->2.8)，更新了部分代码，新的依赖包为req0825
guidance是直接对message生成回复的，所以在muagent\llm_models\openai_model.py的__call__中进行修改
跑examples\muagent_examples\codeToolReact_example.py的时候报错:
Traceback (most recent call last):
  File "D:\CodeFuse-muAgent-main\examples\muagent_examples\codeToolReact_example.py", line 74, in <module>
    query = Message(tools=tools)
            ^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\lenovo\.conda\envs\CF_test\Lib\site-packages\pydantic\main.py", line 193, in __init__
    self.__pydantic_validator__.validate_python(data, self_instance=self)
TypeError: BaseModel.validate() takes 2 positional arguments but 3 were given

认为原因是：
tools: List[BaseTool] = []与pydantic不兼容
但不知道but 3 were given的具体内容是什么，或者怎么才能看到，没能解决


