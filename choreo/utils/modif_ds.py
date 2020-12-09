import numpy as np


def listdict_to_dictlist(_dict, op="compact"):
    """
    리스트를 value로 갖고 있는 딕셔너리 계층구조
     -> 딕셔너리들의 리스트로 바꾸는 함수
    """
    if op not in ("compact", "extended"):
        raise Exception("No such an option")

    max_len = max([len(v) for v in _dict.values()])
    return ([{k: _dict[k][i] for k in _dict.keys() if i < len(_dict[k])} for i in
             range(max_len)] if op != "extended" else [
        {k: (_dict[k][i] if i < len(_dict[k]) else "") for k in _dict.keys()} for i in range(max_len)])


def dictlist_to_listdict(_list):
    """
    딕셔너리들이 원소인 리스트
     -> 각 딕셔너리(원소)에 존재하는 키에 대한 value 리스트로 구성되어있는 딕셔너리
    """
    keyset = {}
    for d in _list:
        keyset = {*keyset, *d}
    # dictionary comprehension -> make res
    ret = {k: [dicit.get(k) for dicit in _list if bool(dicit.get(k))] for k in keyset}
    print(ret)
    return ret


def join_list(list_1, list_2, start_1, stop_1, start_2, stop_2):
    l1 = sorted(np.transpose(np.transpose(list_1).tolist()[start_1:stop_1]).tolist())
    l2 = sorted(np.transpose(np.transpose(list_2).tolist()[start_2:stop_2]).tolist())
    join_key = sorted(list(set(np.transpose(l1).tolist()[0]) & set(np.transpose(l2).tolist()[0])))

    result = []
    for j in l1:
        if j[0] in join_key:
            result += [j]
    t_res = np.transpose(result).tolist()
    # print(t_res)

    for n in l2:
        if n[0] in t_res[0]:
            idx = (t_res[0].index(n[0]))
            print(idx)
            result[idx] += n[1:]
            t_res[0].pop(idx)
            print(t_res[0])

    return result


if __name__ == '__main__':
    li1 = [
        ["dkfjdkfjㅡ13", "absdbvo23kㅡ4", "e_sdkjfkdj", 29],
        ["zdfsdjㅡ3", "sdkf0o23kㅡ4", "s_sdkjfkdj", 14],
        ["kfjㅡ30", "sdkf0o23kㅡ4", "s_sdkjfkdj", 17],
        ["asdbdbㅡ109", "dfgsb3kㅡ4", "s_sdkjfkdj", 19],
        ["erwer234r2", "sdkf0o23kㅡ4", "bbwer23", 51],
        ["sdbkfjㅡ13", "absdbvo23kㅡ4", "s_sdkjfkdj", 29]
    ]
    li2 = [
        ["sdkf0o23kㅡ4", "o23ioo2m", 10],
        ["absdbvo23kㅡ4", "112111111", 3],
        ["dkzxcvdsf", "222222", 13]
    ]
    # expected_result
    expected_res = [
        ["absdbvo23kㅡ4", "e_sdkjfkdj", "112111111"],
        ["absdbvo23kㅡ4", "s_sdkjfkdj", "3i4u12i3"],
        ["sdkf0o23kㅡ4", "s_sdkjfkdj", "o23ioo2m"],
        ["sdkf0o23kㅡ4", "", ],
        ["sdkf0o23kㅡ4", "", ]
    ]
    print(li1)
    print(li2)
    print(join_list(li1, li2, 1, 3, 0, 2))
