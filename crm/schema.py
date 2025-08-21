import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from graphene import relay
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Customer, Product, Order, OrderItem


# ---------- TYPES ----------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filter_fields = ["id", "email"]
        interfaces = (relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


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
        c = Customer(name=input.name, email=input.email, phone=input.phone or "")
        c.full_clean()
        c.save()
        return CreateCustomer(customer=c, message="Customer created successfully.")


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
                    c = Customer(name=data.name, email=data.email,
                                 phone=data.phone or "")
                    c.full_clean()
                    c.save()
                    created.append(c)
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
        p = Product(name=input.name, price=input.price, stock=input.stock)
        p.full_clean()
        p.save()
        return CreateProduct(product=p)


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


# ---------- QUERIES ----------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)


# ---------- MUTATIONS ----------
class Mutation(graphene.ObjectType):
    create_customer       = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product        = CreateProduct.Field()
    create_order          = CreateOrder.Field()