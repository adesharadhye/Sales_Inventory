from django.shortcuts import render, redirect
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        if order.status != 'DRAFT':
            return Response({"error": "Only draft orders can be confirmed"}, status=400)

        with transaction.atomic():
            for item in order.items.select_related('product'):
                inventory = Inventory.objects.select_for_update().get(product=item.product)
                if item.quantity > inventory.quantity:
                    return Response({
                        "error": f"Insufficient stock for {item.product.name}",
                        "available": inventory.quantity,
                        "requested": item.quantity
                    }, status=400)

            for item in order.items.all():
                inventory = Inventory.objects.get(product=item.product)
                inventory.quantity -= item.quantity
                inventory.save()

            order.status = 'CONFIRMED'
            order.save()

        return Response({"status": "Order confirmed"})

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        order = self.get_object()
        if order.status != 'CONFIRMED':
            return Response({"error": "Only confirmed orders can be delivered"}, status=400)
        order.status = 'DELIVERED'
        order.save()
        return Response({"status": "Order delivered"})



def products_page(request):
    return render(request, 'products.html', {
        'products': Product.objects.all()
    })


def dealers_page(request):
    return render(request, 'dealers.html', {
        'dealers': Dealer.objects.all()
    })


def orders_page(request):
    return render(request, 'orders.html', {
        'orders': Order.objects.all()
    })


def inventory_page(request):
    inventory = Inventory.objects.select_related('product').all() # will give all data
    return render(request, 'inventory.html', {'inventory': inventory})


def update_inventory(request): #For handling quantity Undate_inventory
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("quantity_"):
                inventory_id = int(key.split("_")[1])
                inventory = Inventory.objects.get(id=inventory_id)
                inventory.quantity = int(value)
                inventory.save()
        return redirect('inventory_page')


def update_inventory(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("quantity_"):
                inventory_id = int(key.split("_")[1])
                inventory = Inventory.objects.get(id=inventory_id)
                new_quantity = int(value)
                if new_quantity < 0:
                    new_quantity = 0  # Stack should not go Neg
                inventory.quantity = new_quantity
                inventory.save()
        return redirect('inventory_page')


@action(detail=True, methods=['post'])
def confirm(self, request, pk=None):
    order = self.get_object()
    if order.status != 'DRAFT':
        return Response({"error": "Only draft orders can be confirmed"}, status=400)

    with transaction.atomic():
        for item in order.items.select_related('product'):
            inventory = Inventory.objects.select_for_update().get(product=item.product)
            if item.quantity > inventory.quantity:
                return Response({
                    "error": f"Insufficient stock for {item.product.name}",
                    "available": inventory.quantity,
                    "requested": item.quantity
                }, status=400)

        for item in order.items.all(): #Iterating all items 
            inventory = Inventory.objects.get(product=item.product)
            inventory.quantity -= item.quantity
            inventory.save()

        order.status = 'CONFIRMED'
        order.save()

    return Response({"status": "Order confirmed"})


@action(detail=True, methods=['post'])
def deliver(self, request, pk=None):
    order = self.get_object()
    if order.status != 'CONFIRMED':
        return Response({"error": "Only confirmed orders can be delivered"}, status=400)
    order.status = 'DELIVERED'
    order.save()
    return Response({"status": "Order delivered"})



def staff_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('inventory_page')
        else:
            messages.error(request, "Invalid credentials or not authorized")

    return render(request, "login.html")


def is_staff_user(user):
    return user.is_staff

@login_required(login_url='login')
@user_passes_test(is_staff_user, login_url='login')
def inventory_page(request):
    inventory = Inventory.objects.select_related('product').all()
    return render(request, 'inventory.html', {'inventory': inventory})
