from django.contrib import admin
from .models import Product,ProductItem,Order,Category,BillingAddress,PaymentDetails,CouponCode
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordered')

admin.site.register(Product)
admin.site.register(ProductItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Category)
admin.site.register(BillingAddress)
admin.site.register(PaymentDetails)
admin.site.register(CouponCode)
