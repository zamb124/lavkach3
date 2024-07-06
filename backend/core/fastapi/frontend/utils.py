from httpx import QueryParams


def clean_filter(qp: QueryParams | dict, _filter: str) -> list:
    """
        Отбирает параметры согласно фильтру
    """
    models: dict = {}
    new_qp: dict = {}
    keys_to_pop = []
    for k, v in qp.items():
        if not k.startswith(_filter):
            continue
        if v == '':
            qp[k] = None  # type: ignore
        model, line_number, field_name = k.split('--')[:3]
        if len(k.split('--')) == 3:
            if not models.get(model):
                models.update({model: {line_number: {field_name: qp[k]}}})
            else:
                if not models[model].get(line_number):
                    models[model] = {line_number: {field_name: qp[k]}}
                else:
                    models[model][line_number].update({field_name: qp[k]})
            keys_to_pop.append(k)
        elif len(k.split('--')) == 5:
            _model, _line_number, _field_name = k.split('--')[2:5]
            if not models.get(model):
                models.update({model: {line_number: {field_name: {_line_number: {_field_name: qp[k]}}}}})
            else:
                if not models[model].get(line_number):
                    models[model].update({line_number: {field_name: {_line_number: {_field_name: qp[k]}}}})
                else:
                    if not models[model][line_number].get(field_name):
                        models[model][line_number].update({field_name: {_line_number: {_field_name: qp[k]}}})
                    else:
                        if not models[model][line_number][field_name].get(_line_number):
                            models[model][line_number][field_name].update({_line_number: {_field_name: qp[k]}})
                        else:
                            models[model][line_number][field_name][_line_number].update({_field_name: qp[k]})


            keys_to_pop.append(k)
    models_cleaned = []
    for k, v in models.items():
        for _k, _v in v.items():
            models_cleaned.append(_v)
            for __k, __v in _v.items():
                if isinstance(__v, dict):
                    l = []
                    for ___k, ___v in __v.items():
                        l.append(___v)
                    _v[__k] = l

    return models_cleaned
