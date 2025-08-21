import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order, OrderItem

# Clear old data
Customer.objects.all().delete()
Product.objects.all().delete()
Order.objects.all().delete()

# Sample customers
Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
Customer.objects.create(name="Bob",   email="bob@example.com")

# Sample products
p1 = Product.objects.create(name="Laptop", price=999.99, stock=10)
p2 = Product.objects.create(name="Mouse",  price=25.50,  stock=100)

# Sample order
order = Order.objects.create(customer_id=1, total_amount=p1.price + p2.price)
OrderItem.objects.create(order=order, product=p1)
OrderItem.objects.create(order=order, product=p2)

print("Database seeded 🌱")