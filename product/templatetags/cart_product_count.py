from django import template

from product . models import ProductItem
import logging
logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def cart_product_count(user):
    qty = 0
    if user.is_authenticated:
        items = ProductItem.objects.filter(user=user,ordered=False)
        if items.exists():
            for item in items:
                qty += item.quantity         
            return qty
    
    return qty