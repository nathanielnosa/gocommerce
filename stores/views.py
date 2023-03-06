from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from .models import *
from . forms import CheckoutForm
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    # carousel
    banner = Carousel.objects.all()
    # category
    category = Category.objects.all().order_by('-create_at')[:3]
    # latest products
    products = Product.objects.all().order_by('-create_at')[:4]
    context = {
        'banner':banner,
        'categorys':category,
        'latestproducts':products
    }
    return render(request, 'stores/index.html',context)

def products(request):
    # all products
    products = Product.objects.all().order_by('-create_at')
    # paginator
    paginator = Paginator(products,4)
    page_number = request.GET.get('page')
    page_list = paginator.get_page(page_number)

    context={
        'products':products,
        'paginator':page_list
    }
    return render(request, 'stores/store.html',context)

def product(request,id):
    product = Product.objects.get(id=id)
    context={
        'product':product
    }
    return render(request, 'stores/singleproduct.html',context)

# add to cart
def add_to_cart(request,id):
    # get the product
    cart_product = Product.objects.get(id=id)
    # check if cart exist
    cart_id = request.session.get('cart_id',None)
    if cart_id:
        cart_item =Cart.objects.get(id=cart_id)
        # check if product exist
        this_product_in_cart = cart_item.cartproduct_set.filter(product=cart_product)
        # assign cart to customer
        if request.user.is_authenticated and request.user.customer:
            cart_item.customer = request.user.customer
            cart_item.save()

        if this_product_in_cart.exists():
            cartproduct = this_product_in_cart.last()
            cartproduct.quantity +=1
            cartproduct.subtotal += cart_product.price
            cartproduct.save()
            cart_item.total +=cart_product.price
            cart_item.save()
            messages.success(request,'item increased in cart')
        else:
            cartproduct = CartProduct.objects.create(cart=cart_item,product=cart_product,quantity=1,subtotal=cart_product.price)
            cart_item.total += cart_product.price
            cart_item.save()
            messages.success(request,'new item added in cart')


    else:
        cart_item = Cart.objects.create(total=0)
        request.session['cart_id'] = cart_item.id
        cartproduct = CartProduct.objects.create(cart = cart_item, product = cart_product,quantity=1,subtotal =cart_product.price)
        cart_item .total += cart_product.price
        cart_item.save()
        messages.success(request, 'New item to cart added successfully')
    
    return redirect('index')

def myCart(request):
    # session
    cart_id = request.session.get('cart_id',None)
    if cart_id:
        cart_item = Cart.objects.get(id = cart_id)

        if request.user.is_authenticated and request.user.customer:
            cart_item.customer = request.user.customer
            cart_item.save()

    else:
        cart_item = None
    context={
        'cart':cart_item
    }
    return render(request, 'stores/mycart.html',context)

def manageCart(request,id):
    action = request.GET.get('action')
    cart_obj = CartProduct.objects.get(id=id)
    cart = cart_obj.cart

    if action == 'inc':
        cart_obj.quantity +=1
        cart_obj.subtotal += cart_obj.product.price
        cart_obj.save()
        cart.total += cart_obj.product.price
        cart.save()
        messages.success(request, 'Item increased')

    if action == 'dcr':
        cart_obj.quantity -=1
        cart_obj.subtotal -= cart_obj.product.price
        cart_obj.save()
        cart.total -= cart_obj.product.price
        cart.save()
        messages.success(request, 'Item decreased')

        if cart_obj.quantity == 0:
            cart_obj.delete()

    if action == 'rmv':
        cart.total -= cart_obj.subtotal
        cart.save()
        cart_obj.delete()

    else:
        pass    
    return redirect('my_cart')

# checkout
def checkout(request):
    cart_id = request.session.get('cart_id', None)
    cart_obj = Cart.objects.get(id = cart_id)
    form = CheckoutForm()

    # checking authentication
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect('/user/login/?next=/checkout/')

    if request.method == "POST":
        form = CheckoutForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit = False)
            form.cart = cart_obj
            form.amount = cart_obj.total
            form.subtotal = cart_obj.total
            form.discount = 0
            form.order_status = 'pending'
            paymethod = form.payment_method
            del request.session['cart_id']
            paymethod = form.payment_method
            form.save()

            order = form.id
            if paymethod == 'paystack':
                return redirect('payment', id =order)

    context = {
        'cart':cart_obj,
        'form':form
    }
    return render(request, 'stores/checkout.html',context)


def paymentPage(request,id):
    orders = Order.objects.get(id=id)
    context = {
        'order':orders,
        'paystack_public_key' : settings.PAYSTACK_PUBLIC_KEY
    }
    return render(request, 'stores/payment.html',context)


def verify_payment(request:HttpRequest, ref:str) -> HttpResponse:
    payment = get_object_or_404(Order, ref =ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, 'Verification Successful')
    else:
        messages.error(request, 'Verification Failed')
    return redirect('dashboard')
