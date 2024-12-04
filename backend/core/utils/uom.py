from decimal import Decimal, ROUND_HALF_UP


def calculate_quantity(uom_in_type, uom_in_ratio, uom_out_type, uom_out_ratio, uom_out_precision, quantity_in):
    quantity_in = Decimal(quantity_in)
    if uom_in_type == 'smaller':
        quantity_in /= uom_in_ratio
    elif uom_in_type == 'bigger':
        quantity_in *= uom_in_ratio

    if uom_out_type == 'smaller':
        quantity_out = quantity_in * uom_out_ratio
    elif uom_out_type == 'bigger':
        quantity_out = quantity_in / uom_out_ratio
    else:
        quantity_out = quantity_in

    # Округление результата согласно precision
    precision = Decimal('1.' + '0' * int(uom_out_precision))
    quantity_out = quantity_out.quantize(precision, rounding=ROUND_HALF_UP)

    return float(quantity_out)
