from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from . models import Product,ProductItem,Order, BillingAddress,PaymentDetails,CouponCode
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from . forms import CheckoutForm,CouponForm
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

import logging
logger = logging.getLogger(__name__)

# Create your views here.

def HomePage(request):
    context = {
        "product": "test"
    }
    return render(request, 'landingpage.html', {})

class ShopPageView(ListView):
    model = Product
    template_name = "home-page.html"
    context_object_name = "products"
    paginate_by = 16

class ProductPageView(DetailView):
    model = Product
    template_name = "product-page.html"
    context_object_name = "product"

class OrderSummaryView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            if order.product_items.count() == 0:
                messages.info(self.request, "You do not have any orders")
                return redirect("/")
            return render(self.request,"order-summary.html",{"order":order})
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have any orders")
            return redirect("/")

class PaymentView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            if order.product_items.count() == 0:
                messages.info(self.request, "You do not have any orders")
                return redirect("/")
            if order.billingaddress:
                if kwargs.get("payment_option") == 'stripe':
                    return render(self.request,"payment.html",{'order':order})
                elif kwargs.get("payment_option") == 'paypal':
                    messages.info(self.request, "We are not accepting paypal accounts transaction")
                    return redirect("/")
                else:
                    messages.info(self.request, "Unable to redirect to payment page invalid link")
                    return redirect("/")
            
            else:
                messages.warning(self.request,"You do not have any active Billing address")
                return redirect("product:CheckoutPage")

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have any orders")
            return redirect("/")
    
    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            token = self.request.POST.get('stripeToken')
            amount = int(order.total_order_price())
            transaction = stripe.Charge.create(
                amount= amount * 100, #it takes the amount in cents see stripe doc charges
                currency="usd",
                source=token,
                description="My First Test Charge (created for API docs)",
            )

            #set ordered true that order is been placed

            #create payment details 
            payment = PaymentDetails(
                user=self.request.user,
                stripe_transaction_id = transaction.id,
                amount = amount
            )
            payment.save()

            #set all product items as ordered
            for product_item in order.product_items.all():
                product_item.ordered = True
                product_item.save()

            #save payment details to order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request,"Your order was successfully placed")
            return redirect("/")

        except stripe.error.CardError as e:
            messages.error(self.request,f"{e.error.message}")

            # print('Status is: %s' % e.http_status)
            # print('Type is: %s' % e.error.type)
            # print('Code is: %s' % e.error.code)
            # # param is '' in this case
            # print('Param is: %s' % e.error.param)
            # print('Message is: %s' % e.error.message)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request,"Too many requests made to the API too quickly")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request,"Invalid parameters were supplied to Stripe's API")
            return redirect("/")
            
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request,"Authentication with Stripe's API failed")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request,"Network communication with Stripe failed")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request,"Display a very generic error to the user, and maybe send")
            return redirect("/")

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request,"Something else happened, completely unrelated to Stripe")
            return redirect("/")


class CheckOutPageView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            
            checkoutform = CheckoutForm()
            couponform = CouponForm()

            if order.product_items.count() == 0:
                messages.info(self.request, "You do not have any orders")
                return redirect("/")
            return render(self.request,"checkout-page.html",{"order":order,"form":checkoutform,"couponform":couponform})
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have any orders")
            return redirect("/")
    
    def post(self, *args, **kwargs):
        checkoutform = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            if checkoutform.is_valid():
                street_address = checkoutform.cleaned_data.get('street_address')
                apartment_address = checkoutform.cleaned_data.get('apartment_address')
                zipcode = checkoutform.cleaned_data.get('zipcode')
                country = checkoutform.cleaned_data.get('country')
                mobile_no = checkoutform.cleaned_data.get('mobile_no')
                first_name = checkoutform.cleaned_data.get('first_name')
                last_name = checkoutform.cleaned_data.get('last_name')
                # email = checkoutform.cleaned_data.get('email')
                # same_billing_address = checkoutform.cleaned_data.get('same_billing_address')
                save_info = checkoutform.cleaned_data.get('save_info')
                payment_option = checkoutform.cleaned_data.get('payment_option')

                billingaddress = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    zipcode = zipcode,
                    country = country,
                    mobile_no = mobile_no,
                    first_name = first_name,
                    last_name = last_name,
                    is_shipping_address = save_info
                )
                billingaddress.save()
                order.billingaddress = billingaddress
                order.save()
                # redirect to respective payment page
                if payment_option  == 'stripe':
                    return redirect("product:PaymentPage", payment_option = payment_option)
                elif payment_option == 'paypal':
                    messages.info(self.request,"we are not accepting pay pal accounts yet")
                    return redirect("/")
                else:
                    messages.info(self.request,"Invalid payment link")
                    return redirect("/")
            messages.warning(self.request,"Something went wrong please contact administrator")
            return redirect("product:CheckoutPage")
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have any orders")
            return redirect("/")



@login_required
def add_to_cart(request,slug):
    quantity = int(request.GET.get('quantity',1))
    product = get_object_or_404(Product,slug=slug) 
    order_item,created = ProductItem.objects.get_or_create(product=product,user=request.user,ordered=False)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.product_items.filter(product__slug=product.slug).exists():
            order_item.quantity += quantity
            order_item.save()
            messages.info(request, "The Product is quantity is updated your cart")
        else:
            order_item.quantity = quantity
            order_item.save()
            order.product_items.add(order_item)
            messages.info(request, "The Product is added in your cart")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order_item.quantity = quantity
        order_item.save()
        order.product_items.add(order_item)
        messages.info(request, "The Product is added in your cart")
    
    return redirect("product:ProductPage", slug=slug)

@login_required
def remove_cart_product(request,slug):
    product = get_object_or_404(Product,slug=slug)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.product_items.filter(product__slug=product.slug).exists():
            order_item = ProductItem.objects.filter(product=product,user=request.user,ordered=False)[0]
            order_item.delete()
            messages.info(request, "The Product is removed from your cart")

        else:
            messages.info(request, "The Product is not in your cart")
            return redirect("product:OrderSummary")
    else:
        messages.info(request, "You do not have any orders yet")
        return redirect("product:OrderSummary")
    
    return redirect("product:OrderSummary")

@login_required
def remove_qty_from_cart(request,slug):
    product = get_object_or_404(Product,slug=slug) 
    order_item = ProductItem.objects.get(product=product,user=request.user,ordered=False)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.product_items.filter(product__slug=product.slug).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "The Product is quantity is updated your cart")
    
    return redirect("product:OrderSummary")

@login_required
def add_qty_to_cart(request,slug):
    product = get_object_or_404(Product,slug=slug) 
    order_item = ProductItem.objects.get(product=product,user=request.user,ordered=False)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.product_items.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "The Product is quantity is updated your cart")
    
    return redirect("product:OrderSummary")

def remove_coupon(request):
    try:
        order = Order.objects.get(user=request.user,ordered=False)
        order.coupon_applied = None
        order.save()
        messages.info(request, "The Coupon code is removed successfully")
        return redirect("product:CheckoutPage")

    except ObjectDoesNotExist:
        messages.info(request, "The Coupon code is invalid")
        return redirect("product:CheckoutPage")

def get_coupon(request, code):
    coupon_code = CouponCode.objects.get(code=code)
    return coupon_code

def apply_coupon(request):
    if request.method =='POST':
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user,ordered=False)
                order.coupon_applied = get_coupon(request,code)
                order.save()
                messages.info(request,"The coupon has been applied")
                return redirect("product:CheckoutPage")

            except ObjectDoesNotExist:
                messages.info(request, "The Coupon code is invalid")
                return redirect("product:CheckoutPage")

    #raise an error as get request is made to coupons which is not allowed because its a form
    return None
