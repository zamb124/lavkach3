from fastapi_htmx import TemplateSpec as ts
def s(template_name):
    """
    Трансформирует модуль и имя темплейта в спеки для htmx
    Просто для сокращения
    """
    return (
        template_name,
        f'{template_name}-full'
    )