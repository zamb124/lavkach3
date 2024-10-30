from starlette.requests import Request

from core.frontend.constructor import ClassView, BaseSchema


class OrderView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['order_list']
        super().__init__(request=request, model='order', permits=permits)


class MoveView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['move_list']
        super().__init__(request=request, model='move', permits=permits)

class OrderTypeView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['order_type_list']
        super().__init__(request=request, model='order_type', permits=permits)

class StoreView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['store_list']
        super().__init__(request=request, model='store', permits=permits)

