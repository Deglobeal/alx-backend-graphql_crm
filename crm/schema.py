# crm/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Customer, Product, Order, OrderItem
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product
from django.db.models import Sum

# ---------- TYPES ----------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (relay.Node,)
        fields = ("id", "name", "stock", "price")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (relay.Node,)


# ---------- INPUTS ----------
class CustomerInput(graphene.InputObjectType):
    name  = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CustomerListInput(graphene.InputObjectType):
    name  = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name  = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)


# ---------- MUTATIONS ----------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message  = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists.")
        customer = Customer(name=input.name, email=input.email,
                            phone=input.phone or "")
        customer.full_clean()
        customer.save()
        return CreateCustomer(customer=customer,
                              message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerListInput, required=True)

    customers = graphene.List(CustomerType)
    errors    = graphene.List(graphene.String)

    def mutate(self, info, input):
        created, errors = [], []
        with transaction.atomic():
            for data in input:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        errors.append(f"{data.email} already exists.")
                        continue
                    cust = Customer(name=data.name, email=data.email,
                                    phone=data.phone or "")
                    cust.full_clean()
                    cust.save()
                    created.append(cust)
                except ValidationError as ve:
                    errors.extend(ve.messages)
        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive.")
        if input.stock < 0:
            raise ValidationError("Stock must be non-negative.")
        product = Product(name=input.name,
                          price=input.price,
                          stock=input.stock)
        product.full_clean()
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID.")
        if not input.product_ids:
            raise ValidationError("At least one product is required.")

        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise ValidationError("One or more product IDs are invalid.")

        with transaction.atomic():
            order = Order(customer=customer)
            order.save()
            order.products.set(products)
            order.total_amount = sum(p.price for p in products)
            order.save()
        return CreateOrder(order=order)


class UpdateLowStockProducts(graphene.Mutation):
    """
    Mutation to update the stock of products with stock < 10.
    Adds 10 units to each low-stock product.
    """
    updated_count = graphene.Int()
    products = graphene.List(ProductType)

    class Arguments:
        # Optional: allow overriding default increment of 10
        increment = graphene.Int(default_value=10)

    def mutate(self, info, increment=10):
        from crm.models import Product  # Ensure model is available
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_count = low_stock_products.update(stock=10)

        return UpdateLowStockProducts(
            updated_count=updated_count,
            products=list(low_stock_products)
        )



# ---------- QUERIES ----------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products  = DjangoFilterConnectionField(ProductType)
    all_orders    = DjangoFilterConnectionField(OrderType)
    totalCustomers = graphene.Int()
    totalOrders    = graphene.Int()
    totalRevenue   = graphene.Float()

    def resolve_totalCustomers(root, info):
        return Customer.objects.count()

    def resolve_totalOrders(root, info):
        return Order.objects.count()

    def resolve_totalRevenue(root, info):
        return Order.objects.aggregate(total=Sum('totalamount'))['total'] or 0


# ---------- MUTATIONS ----------
class Mutation(graphene.ObjectType):
    create_customer       = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product        = CreateProduct.Field()
    create_order          = CreateOrder.Field()