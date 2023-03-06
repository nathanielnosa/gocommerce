from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate

from . forms import CustomerProfile
from stores.models import Order
# Create your views here.
def loginuser(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')

        user = authenticate(username = username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, 'User logged in successfully')
        
            if "next" in request.GET:
                    next_url=request.GET.get("next")
                    return redirect(next_url)
            else:
                return redirect('login')
            

    return render(request, 'users/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    profile = CustomerProfile()
    if request.method == 'POST':        
        form  = CustomerProfile(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            if password != password2:
                messages.error(request, 'Password not match')
                return redirect('register')

            if User.objects.filter(username = username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')

            if User.objects.filter(email = email).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')
            
            user = User.objects.create_user(username,email,password)
            form = form.save(commit=False)
            form.user = user

            form.save()
            messages.success(request, 'User has been created successfully !')
        

            if "next" in request.GET:
                next_url=request.GET.get("next")
                return redirect(next_url)
            else:
                return redirect('login')
    context={
        'form':profile
    }
    return render(request, 'users/register.html', context)

def logoutuser(request):
    logout(request)
    return redirect('index')

def dashboard(request):
    user = request.user.username

    context ={
        'user':user
    }
    return render(request, 'users/dashboard.html',context)

def orders(request):
    if request.user.is_authenticated and request.user.customer:
        pass
    else:
        return redirect('login')

    customer = request.user.customer
    orders = Order.objects.filter(cart__customer = customer).order_by('-id')
    context = {
        'orders':orders,
    }

    return render(request, 'users/order.html',context)