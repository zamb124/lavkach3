from app.basic import __domain__ as basic_domain
from app.inventory import __inventory_manifest__ as inventory_domain
from core.core_apps.base import __domain__ as base_domain

domains: list = [base_domain, inventory_domain, basic_domain, inventory_domain]
