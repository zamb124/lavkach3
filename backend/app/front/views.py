from app.front.utills import BaseClass

"""
Переопределяем классы как депенденсы
"""

class Order(BaseClass):
    """Переопределяем модель"""
    model_name = "order"
    permits = ['order_list']

