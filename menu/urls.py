# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('load-dishes/<int:category_id>/', views.load_dishes, name='load_dishes'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),

    path('get-cart/', views.get_cart, name='get_cart'),]
