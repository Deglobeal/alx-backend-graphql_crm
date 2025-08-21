import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order, OrderItem

# Clear tables that have FK dependencies first
OrderItem.objects.all().delete()
Order.objects.all().delete()
Customer.objects.all().delete()
Product.objects.all().delete()

# 1) Customers
c1 = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
c2 = Customer.objects.create(name="Bob",   email="bob@example.com")

# 2) Products
p1 = Product.objects.create(name="Laptop",  price=999.99, stock=10)
p2 = Product.objects.create(name="Mouse",   price=25.50,  stock=100)
p3 = Product.objects.create(name="Keyboard",price=75.00,  stock=50)

# 3) Order
order = Order.objects.create(customer=c1, total_amount=p1.price + p2.price)
OrderItem.objects.create(order=order, product=p1)
OrderItem.objects.create(order=order, product=p2)

print("Database seeded 🌱")