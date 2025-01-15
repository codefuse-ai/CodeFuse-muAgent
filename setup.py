import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="codefuse-muagent",
    version="0.1.1",
    author="shanshi",
    author_email="wyp311395@antgroup.com",
    description="An Innovative Agent Framework Driven by KG Engine",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codefuse-ai/CodeFuse-muAgent",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "openai==1.34.0",
        "langchain==0.2.3",
        "langchain_community==0.2.4",
        "langchain_openai==0.1.8",
        "langchain_huggingface==0.0.3",
        "sentence_transformers",
        "loguru",
        "fastapi",
        "pandas",
        "Pyarrow",
        "jieba",
        "psutil",
        "faiss-cpu",
        "notebook",
        "docker",
        "sseclient",
        "edit_distance",
        "urllib3==1.26.6",
        "ollama",
        "colorama",
        "pycryptodome",
        "dashscope",
        # 
        "chromadb==0.4.17",
        "javalang==0.13.0",
        "nebula3-python==3.8.2",
        "SQLAlchemy==2.0.19",
        "redis==5.0.1",
        "pydantic<=1.10.14",
        "aliyun-log-python-sdk==0.9.0"
    ],
)