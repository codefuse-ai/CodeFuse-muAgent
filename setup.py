import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="codefuse-muagent",
    version="0.0.5",
    author="shanshi",
    author_email="wyp311395@antgroup.com",
    description="A multi-agent framework that facilitates the rapid construction of collaborative teams of agents.",
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
        # 
        "chromadb==0.4.17",
        "javalang==0.13.0",
        "nebula3-python==3.1.0",
        "SQLAlchemy==2.0.19",
        "redis==5.0.1",
        "pydantic<=1.10.14"
    ],
)