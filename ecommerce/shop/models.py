from django.db import models
from django.contrib.auth.models import User
import uuid
from django_stubs_ext.db.models import TypedModelMeta

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta(TypedModelMeta):
        verbose_name = "Product"
        verbose_name_plural = "Products"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    items: models.Manager['CartItem']

    class Meta(TypedModelMeta):
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    class Meta(TypedModelMeta):
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')

    class Meta(TypedModelMeta):
        verbose_name = "Order"
        verbose_name_plural = "Orders"