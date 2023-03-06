from django.db import models

from users.models import Customer
from django.contrib.auth.models import User
import secrets
from . paystack import Paystack
# Create your models here.

class Carousel(models.Model):
    image = models.ImageField(upload_to='slider')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return str(self.created_at)
    
class Category(models.Model):
    title = models.CharField(max_length=225)
    create_at = models.DateTimeField(auto_now_add=True, null=True)

    
    def __str__(self):
        return self.title
    

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='product')
    category = models.ForeignKey(Category,on_delete=models.SET_DEFAULT, default='Null')
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.title
    
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
    total = models.PositiveIntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{str(self.total)}'
    
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity= models.PositiveSmallIntegerField()
    subtotal = models.PositiveIntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Cart -{self.cart.id}'

ORDER_STATUS=(
    ('completed','completed'),
    ('pending','pending'),
    ('cancelled','cancelled'),
)

PAYMENT_METHOD=(
    ('paystack','paystack'),
    ('transfer','transfer'),
)
class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE , null=True)
    order_by = models.CharField(max_length=255)
    shipping_address = models.TextField()
    mobile = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    discount = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=225, choices=ORDER_STATUS,null=True)
    payment_method = models.CharField(max_length=225, choices=PAYMENT_METHOD,null=True, default='paystack')
    payment_complete = models.BooleanField(default=False,null=True)
    ref = models.CharField(max_length=255,null=True)
    
    
    def __str__(self) -> str:
        return f'{self.order_status}:: {str(self.id)}'
    # ref generate
    def save(self,*args,**kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            obj_with_sm_ref = Order.objects.filter(ref=ref)
            if not obj_with_sm_ref:
                self.ref = ref
        super().save(*args,**kwargs)

    def amount_value(self)-> int:
        return self.amount * 100
    
    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.payment_complete = True
            self.save()
        if self.payment_complete:
            return True
        return False
