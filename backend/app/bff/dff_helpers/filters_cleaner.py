from httpx import QueryParams


def clean_filter(qp: QueryParams|dict, filter:str):
    """
        Отбирает параметры согласно фильтру
    """
    new_qp = {}
    for k, v in qp.items():
        if v == '': continue
        if k.startswith(filter):
            k = k.split(filter)[1]
        new_qp.update({k: v})
    new_qp.pop('prefix')
    if new_qp.get('search_terms'):
        new_qp.pop('search_terms')
    return new_qp