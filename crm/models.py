from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Customer(models.Model):
    name  = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{1,4}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3}[\s\-]?\d{4,}$',
                message="Phone must be in format '+1234567890' or '123-456-7890'."
            )
        ] )
    created_at = models.DateTimeField(auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Product(models.Model):
    name  = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer   = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                   related_name="orders")
    products   = models.ManyToManyField(Product, through='OrderItem')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       default=0.00)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.name}"


class OrderItem(models.Model):
    order   = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)