from pydantic import BaseModel
from starlette.requests import Request

from core.frontend.constructor import ClassView, views


class OrderView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['order_list']
        super().__init__(request=request, model='order')


class MoveView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['move_list']
        super().__init__(request=request, model='move',)


class SuggestView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['suggest_list']
        super().__init__(request=request, model='suggest')


class MoveLogView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['move_log_list']
        super().__init__(request=request, model='move_log')


class OrderTypeView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['order_type_list']
        super().__init__(request=request, model='order_type')


class StoreView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['store_list']
        super().__init__(request=request, model='store')
        self.h.templates.update({
            'as_modal': 'basic/store/as_modal.html',
        })


class StoreStaffView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['store_staff_list']
        super().__init__(request=request, model='store_staff')


views.update({
    'order': OrderView,
    'move': MoveView,
    'order_type': OrderTypeView,
    'store': StoreView,
    'store_staff': StoreStaffView
})
