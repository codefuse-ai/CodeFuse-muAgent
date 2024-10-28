import math
import hashlib

def normalize(lis):
    s = sum([i * i for i in lis])
    if s == 0:
        raise ValueError('Sum of lis is 0')

    s_sqrt = math.sqrt(s)
    res = [i / s_sqrt for i in lis]
    return res
def md5_hash(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()
def hash_id(nodeId, sessionId='', otherstr = None):
    test_res = ''
    test_all = nodeId + sessionId 
    test_res = test_res + (md5_hash(test_all))
    if otherstr == None:
        return test_res
    else:
        test_res = test_res + otherstr
        return test_res



if __name__ == '__main__':
    # hash_id 
    # text = "Hello, World!"
    # print("MD5 Hash of '{}' is: {}".format(text, md5_hash(text)))
    # print(md5_hash(text))

    #hash_id
    nodeId = "剧本杀/谁是卧底"
    #sessionId = 'bbbb'
    #otherstr  = '-userInput'
    print(hash_id(nodeId))