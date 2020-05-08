# from django.contrib import admin
from django.urls import path
from .import views

app_name = "product"

urlpatterns = [
    path('', views.HomePage, name="HomePage"),
    path('remove_coupon/', views.remove_coupon, name="RemoveCoupon"),
    path('get_coupon/', views.apply_coupon, name="Coupon"),
    path('shop/', views.ShopPageView.as_view(), name="ShopPage"),
    path('checkout/', views.CheckOutPageView.as_view(), name="CheckoutPage"),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name="PaymentPage"),
    path('ordersummary/', views.OrderSummaryView.as_view(), name="OrderSummary"),
    path('product/<slug:slug>/', views.ProductPageView.as_view(), name="ProductPage"),
    path('addtocart/<slug:slug>/', views.add_to_cart, name="AddToCart"),
    path('removecartproduct/<slug:slug>/', views.remove_cart_product, name="RemoveCartProduct"),
    path('removeqtyproduct/<slug:slug>/', views.remove_qty_from_cart, name="RemoveQtyProduct"),
    path('addqtyproduct/<slug:slug>/', views.add_qty_to_cart, name="AddQtyProduct"),
]
