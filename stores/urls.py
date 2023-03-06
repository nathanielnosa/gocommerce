from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('products/',views.products,name='products'),
    path('product/<str:id>/',views.product,name='product'),
    path('add_to_cart/<str:id>/',views.add_to_cart,name='add_to_cart'),
    path('my_cart',views.myCart,name='my_cart'),
    path('manageCart/<str:id>/',views.manageCart,name='manageCart'),
    path('checkout/',views.checkout, name='checkout'),

    path('payment/<str:id>/',views.paymentPage, name='payment'),
    path('<str:ref>/',views.verify_payment, name='verify-payment'),

]