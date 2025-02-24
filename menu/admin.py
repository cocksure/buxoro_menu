from django.contrib import admin

from .models import Category, Dish, Restaurant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'description')
    list_editable = ('display_order',)
    search_fields = ('name',)
    ordering = ('display_order',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'display_order')
    list_editable = ('price', 'is_available', 'display_order')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_available')
    ordering = ('category', 'display_order')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name',)


