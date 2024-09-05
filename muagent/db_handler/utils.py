
def deduplicate_dict(dict_list: list = []):
    seen = set()
    unique_dicts = []
    
    for d in dict_list:
        # 使用 frozenset 进行较快的哈希，并避免重复转换
        d_tuple = tuple(sorted(d.items()))
        if d_tuple not in seen:
            seen.add(d_tuple)
            unique_dicts.append(d)
    
    return unique_dicts