from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

# Create your models here.
LBAEL_CHOICES = (
    ('new','New'),
    ('bstseller','Bestseller'),
    ('popular','Popular'),
)

LABEL_COLOR = (
    ('primary-color','Primary'),
    ('secondary-color','Secondary'),
    ('danger-color','Danger'),
    ('purple','Purple'),
)

class Category(models.Model):
    name = models.CharField(max_length=50)
    label_color = models.CharField(choices=LABEL_COLOR, default="purple", max_length=15)
    parent_id = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    mobile_no = models.IntegerField(blank=True,null=True)
    is_shipping_address = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField(blank=True,null=True)
    category = models.ManyToManyField(Category, blank=True)
    label = models.CharField(choices=LBAEL_CHOICES, blank=True, max_length=15)
    slug = models.SlugField()
    description = models.TextField(max_length=300,blank=True)
    discount = models.FloatField(blank=True, null=True)

    def get_product_url(self):
        return reverse("product:ProductPage",kwargs={
            'slug':self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse("product:AddToCart",kwargs={
            'slug':self.slug
        })
    
    def get_remove_cart_product_url(self):
        return reverse("product:RemoveCartProduct",kwargs={
            'slug':self.slug
        })



    def get_label_color(self):
        if self.label == 'popular':
            return 'secondary'
        elif self.label == 'bstseller':
            return 'danger'
        else:
            return 'primary'

    def __str__(self):
        return self.name

class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return "{} of product {}".format(self.quantity,self.product)
    
    def total_product_price(self):
        if self.product.discount:
            price = self.product.discount
        else:
            price = self.product.price
        return self.quantity * price

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_items = models.ManyToManyField(ProductItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billingaddress = models.ForeignKey("BillingAddress", on_delete=models.SET_NULL, blank=True,null=True)
    payment = models.ForeignKey("PaymentDetails", on_delete=models.SET_NULL, blank=True,null=True)
    coupon_applied = models.ForeignKey("CouponCode", on_delete=models.SET_NULL, blank=True,null=True)

    def get_discounted_price(self):
        price = 0
        for item in self.product_items.all():
            price += item.total_product_price()

        return ((self.coupon_applied.offer_percent/100)*price)

    def total_order_price(self):
        price = 0
        for item in self.product_items.all():
            price += item.total_product_price()
        
        if self.coupon_applied:
            price = price - ((self.coupon_applied.offer_percent/100)*price)
        return price

    def __str__(self):
        return self.user.username

class PaymentDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True,null=True)
    stripe_transaction_id = models.CharField(max_length=50)
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class CouponCode(models.Model):
    code = models.CharField(max_length=30)
    offer_percent = models.FloatField()
    
    def __str__(self):
        return self.code