


def compare_lists(list1, list2):
    # Проверка, что количество объектов в списках одинаковое
    if len(list1) != len(list2):
        return False

    # Сортировка списков по id объектов
    list1_sorted = sorted(list1, key=lambda x: x.id)
    list2_sorted = sorted(list2, key=lambda x: x.id)

    # Проверка, что объекты в списках идентичны
    for obj1, obj2 in zip(list1_sorted, list2_sorted):
        if obj1.quantity != obj2.quantity or obj1.available_quantity != obj2.available_quantity:
            return False

    return True