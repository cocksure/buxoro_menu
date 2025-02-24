from django.contrib import admin

from .models import Category, Dish, Restaurant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'image')
    list_editable = ('display_order',)
    search_fields = ('name',)
    ordering = ('display_order',)


class ImageFilter(admin.SimpleListFilter):
    title = ("Наличие изображения")  # Название фильтра
    parameter_name = "has_image"  # Имя параметра в URL

    def lookups(self, request, model_admin):
        return [
            ("yes", ("Есть изображение")),
            ("no", ("Нет изображения")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(image="")  # Фильтруем только с фото
        elif self.value() == "no":
            return queryset.filter(image="")  # Фильтруем только без фото
        return queryset  # Возвращаем все объекты без фильтра


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'category', 'price', 'is_available', 'display_order')
    list_editable = ('price', 'is_available', 'display_order')
    search_fields = ('name',)
    list_filter = ('category', 'is_available', ImageFilter)  # Добавляем новый фильтр
    ordering = ('category', 'display_order')

    actions = ['clear_image']

    @admin.action(description="Очистить изображение")
    def clear_image(self, request, queryset):
        for dish in queryset:
            if dish.image:
                dish.image.delete(save=False)
                dish.image = None
                dish.save(update_fields=['image'])

        self.message_user(request, "Изображение успешно удалено", level="info")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name',)
