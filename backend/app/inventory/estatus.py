def estatus(*statuses):
    """
    Декоратор для установки статуса методу, который его устанавливает
    """
    def decorator(func):
        if not hasattr(func, '_estatus'):
            func._estatus = []
        func._estatus.extend(statuses)
        return func

    return decorator
