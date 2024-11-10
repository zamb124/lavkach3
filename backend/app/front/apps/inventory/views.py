from starlette.requests import Request

from core.frontend.constructor import ClassView, BaseSchema, views


class OrderView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['order_list']
        super().__init__(request=request, model='order', schema=schema, permits=permits)

class MoveView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['move_list']
        super().__init__(request=request, model='move', schema=schema,  permits=permits)

class SuggestView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['suggest_list']
        super().__init__(request=request, model='suggest', schema=schema,  permits=permits)

class MoveLogView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['move_log_list']
        super().__init__(request=request, model='move_log', schema=schema,  permits=permits)

class OrderTypeView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['order_type_list']
        super().__init__(request=request, model='order_type', schema=schema,  permits=permits)

class StoreView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['store_list']
        super().__init__(request=request, model='store', schema=schema,  permits=permits)
        self.h.templates.update({
            'as_modal': 'basic/store/as_modal.html',
        })

class StoreStaffView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['store_staff_list']
        super().__init__(request=request, model='store_staff', schema=schema,  permits=permits)

views.update({
    'order': OrderView,
    'move': MoveView,
    'order_type': OrderTypeView,
    'store': StoreView,
    'store_staff': StoreStaffView
})