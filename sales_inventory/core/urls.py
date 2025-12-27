from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views   

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('dealers', DealerViewSet)
router.register('orders', OrderViewSet)
# router.register('inventory', InventoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('products/', products_page),
    path('dealers/', dealers_page),
    path('orders/', orders_page),
    path('inventory/', inventory_page, name='inventory_page'),
    path('login/', views.staff_login, name='login'),
    path('inventory/update/', update_inventory, name='update_inventory'),
]
