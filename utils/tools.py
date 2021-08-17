
import numpy
import hashlib

def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def set_dict_list(dict_list):
    """
    Remove duplicate dict in given list

    :parm: a list consist with dictionary
    :return: a list removed duplicate dictionary
    """
    # result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in dict_list)]

    seen = set()
    new_l = []
    for d in dict_list:
        t = str(d)
        if t not in seen:
            seen.add(t)
            new_l.append(d)

    return new_l

def remove_same_combination(dict_list):
    """
    Remove the rule that both api are have same name
    
    :parm: a list consist with rule
    :return: a list that removed same api rule
    """

    new_list = []
    for obj in dict_list:
        if not str(obj["api1"]) == str(obj["api2"]):
            new_list.append(obj)
    return new_list

def distribute(seq, sort):
    """
    Equally distribute a list into several list

    :parm:
        seq: the list that be distributed
        sort: a number that distribute in n part 

    :return: a two dimension list of distrubuted
    """
    new_seq = numpy.array_split(seq, sort)
    return new_seq

def api_filter(apk, percentile_rank):
    statistic_result = {}
    api_pool = apk.apis
    for api in api_pool:
        number_from = len(apk.apk_analysis.apkinfo.upperfunc(api))
        statistic_result[api] = number_from

    sorted_result = {k: v for k, v in sorted(statistic_result.items(), key=lambda item: item[1])}
    
    threshold = len(api_pool) * percentile_rank
    api_above = []
    api_under = []
    p_count = {"first": [], "second": []}
    for i, (api, number) in enumerate(sorted_result.items()):
        if i < threshold:
            api_above.append(api)
            p_count["first"].append(number)
            continue
        p_count["second"].append(number)
        api_under.append(api)
        
    return api_above, api_under, p_count