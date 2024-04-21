import os
from muagent.retrieval.text_splitter import LCTextSplitter



cur_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(cur_dir, "text.txt")
lc_textSplitter = LCTextSplitter(filepath)
docs = lc_textSplitter.file2text()

print(docs[0])