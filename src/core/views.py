from django.shortcuts import render,get_object_or_404,redirect
from core.models import (Banner,Brand,Categories,Item,OrderItem,Order,
                        Address,Payment,
                        Coupon,Refund,Wishlist)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib import messages
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import (CouponForm,CheckoutForm,RefundForm)
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from pypaystack import Transaction
from django.conf import settings
import string
import json
import random


# Create your views here.
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'order': order,
                'form':form,
                'couponform' : CouponForm(),
                'DISPLAY_COUPON_FORM': True,   
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
            
            return render(self.request, 'checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request, "you do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    #print("Using the default shipping address")
                    messages.info(self.request, "Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S', 
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    name = form.cleaned_data.get(
                        'name')
                    email = form.cleaned_data.get(
                        'email')
                    address = form.cleaned_data.get(
                        'address')
                    
                    phone_no=form.cleaned_data.get(
                        'phone_no')

                    if is_valid_form([address, name,email,phone_no]):
                        shipping_address = Address(
                            user=self.request.user,
                            name=name,
                            email=email,
                            phone_no=phone_no,
                            address=address,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                            

                payment_option = form.cleaned_data.get('payment_option')
                
                
                if payment_option == 'P':
                    return redirect('core:payment', payment_option='Paystack')
                elif payment_option == 'F':
                    return redirect('core:flutter', payment_option='flutter')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
            else:
                 print("User is entering a new user")
        
        except ObjectDoesNotExist: 

            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class Paymentview(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.shipping_address:
                pk_public = settings.PAYSTACK_PUBLIC_KEY
                context = {
                    'order': order,
                    'pk_public':pk_public,
                    'DISPLAY_COUPON_FORM': False

                    }
                return render(self.request, 'paystack.html ',context)
            else:

                messages.warning(self.request, "You do have not added a billing addres")
                return redirect("core:order-summary")
        except ObjectDoesNotExist:
            pass

def verify(request,id):
    transaction = Transaction(authorization_key=settings.PAYSTACK_SECRET_KEY)
    response= transaction.verify(id)
    data = JsonResponse(response,safe=False)

    order =Order.objects.get(user=request.user, ordered=False)
    payment = Payment()
    payment.stripe_charge_id = response
    payment.user =request.user
    payment.amount = order.get_total()
    payment.save()

    order_items = order.items.all()
    order_items.update(ordered =True)
    for item in order_items:
        item.save()
    order.ordered =True
    order.payment = payment
    order.ref_code = create_ref_code()
    order.save()

    messages.success(request,'your order was succesful' + order.ref_code )
    return redirect ('/')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "core/refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")




class ordersummary(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'shopping-cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return render(self.request, 'shopping-cart.html')

@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order= order_qs[0]
        #check if order item is already ordered

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")

    #if order doesn't exist
    else:
        ordered_date=timezone.now()
        order =Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


    return redirect('core:ordersummary')

@login_required
def remove_from_cart(request,slug):

    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order= order_qs[0]
        #check if order item is already ordered

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                        item=item,
                        user=request.user,
                        ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
        else:
        # item is not part of cart message
            messages.info(request, "This item was not in your cart")
            return redirect('core:product',slug=slug)
    else:
        # no order message
        messages.info(request, "You do not have an active order")
        return redirect('core:product',slug=slug)
    return redirect('core:product',slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('core:product',slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect('core:product',slug=slug)



def Product_Page(request,slug):
    item = get_object_or_404(Item,slug=slug)
    items=Item.objects.filter(category=item.category )

    page = request.GET.get('page', 1)

    paginator = Paginator(items, 8)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


    context = {
        'page_obj':page_obj,
        'item':item
    }
    return render(request,"product-page.html",context)

def about_page(request):
    return render(request,"about-page.html")

def home_page(request):

    banner = Banner.objects.all().order_by("-id")
    category = Categories.objects.all().order_by("name")
    item = Item.objects.all().order_by('-id')
    brands = Brand.objects.all().order_by('name')


    page = request.GET.get('page', 1)

    paginator = Paginator(item, 8)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'banner':banner,
        "categorys":category,
        'page_obj':page_obj,
        'brands':brands,
    }
    return render(request,"home-page.html", context)


def confirm_order(request):
    order = Order.objects.filter(user=request.user).order_by('-id')
    context = {
                'object': order
            }
    return render(request,'ordered_item.html', context)

def wishlist(request):
    wlist=Wishlist.objects.filter(user=request.user).order_by('-id')

    return render(request,'wishlist.html',{'wlist':wlist})

def add_wishlist(request, id):

    product=Item.objects.get(id=id)
    data={}
    checkw=Wishlist.objects.filter(product=product,user=request.user).count()
    if checkw > 0:
        data={
            'bool':False
        }
    else:
        wishlist=Wishlist.objects.create(
            product=product,
            user=request.user
        )
        data={
            'bool':True
        }
    return redirect("core:wishlist")

def delete_wishlist(request, id):

    product=Item.objects.get(id=id)
    data={}
    checkw=Wishlist.objects.filter(product=product,user=request.user)
    
    checkw.delete()
    return redirect('core:wishlist')