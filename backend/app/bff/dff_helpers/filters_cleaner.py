from httpx import QueryParams


def clean_filter(qp: QueryParams|dict, filter:str):
    """
        Отбирает параметры согласно фильтру
    """
    new_qp = {}
    if qp.get('prefix'):
        qp.pop('prefix')
    if qp.get('search_terms'):
        qp.pop('search_terms')
    for k, v in qp.items():
        if v == '': continue
        if k.startswith(filter):
            k = k.split(filter)[1]
        new_qp.update({k: v})
    return new_qp