
from django.contrib import admin
from .models import Category, Dish, Restaurant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'description')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order',)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'order')
    list_editable = ('price', 'is_available', 'order')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_available')
    ordering = ('category', 'order')

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', )