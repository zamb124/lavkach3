from inspect import isclass
from typing import get_origin, get_args

from httpx import QueryParams

from core.frontend.enviroment import passed_classes


def get_types(annotation: object, _class: list = []) -> list[object]:
    """
        Рекурсивно берем типы из анотации типа
    """
    if isclass(annotation):
        _class.append(annotation)
        return _class
    else:
        origin = get_origin(annotation)
        annotate = get_args(annotation)
        if origin and origin not in passed_classes:
            _class.append(origin)
        try:
            get_types(annotate[0], _class)
        except Exception as ex:
            _class.append(annotation)
    return _class


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
            v = None  # type: ignore
        filterred_key = k.replace(_filter, '')
        model, line_number, field_name = filterred_key.split('--')[:3]
        if len(filterred_key.split('--')) == 3:
            if not models.get(model):
                models.update({model: {line_number: {field_name: v}}})
            else:
                if not models[model].get(line_number):
                    models[model].update({line_number: {field_name: v}})
                else:
                    models[model][line_number].update({field_name: v})
            keys_to_pop.append(k)
        elif len(filterred_key.split('--')) == 5:
            _model, _line_number, _field_name = filterred_key.split('--')[2:5]
            if not models.get(model):
                models.update({model: {line_number: {field_name: {_line_number: {_field_name: v}}}}})
            else:
                if not models[model].get(line_number):
                    models[model].update({line_number: {field_name: {_line_number: {_field_name: v}}}})
                else:
                    if not models[model][line_number].get(field_name):
                        models[model][line_number].update({field_name: {_line_number: {_field_name: v}}})
                    else:
                        if not models[model][line_number][field_name].get(_line_number):
                            models[model][line_number][field_name].update({_line_number: {_field_name: v}})
                        else:
                            models[model][line_number][field_name][_line_number].update({_field_name: v})


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
