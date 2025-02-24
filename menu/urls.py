from django.urls import path
from . import views
from .views import RestaurantListView, CategoryListView, DishListView, CartView


urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('load-dishes/<int:category_id>/', views.load_dishes, name='load_dishes'),
    path('add-to-cart/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('get-cart/', views.get_cart, name='get_cart'),

    # ----- API urls ---------
    path('api/restaurants/', RestaurantListView.as_view(), name='restaurant_list'),
    path('api/categories/', CategoryListView.as_view(), name='category_list'),
    path('api/dishes/', DishListView.as_view(), name='dish_list'),
    path('api/dishes/<int:category_id>/', DishListView.as_view(), name='dish_list_by_category'),
    path('api/cart/', CartView.as_view(), name='cart'),

]
