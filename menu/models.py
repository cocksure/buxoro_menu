import os
from PIL import Image
from django.core.files.storage import default_storage
from django.db import models
from django.core.validators import FileExtensionValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    image = models.ImageField(upload_to="category_images/",
                              blank=True, verbose_name="Фото категории",
                              default='default_images/default_foto.png',  # Путь по умолчанию
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic'])])

    def save(self, *args, **kwargs):
        if self.pk:
            # Получаем старое изображение, если оно было
            old_image = Category.objects.get(pk=self.pk).image

            # Если новое изображение задано, и оно отличается от старого
            if self.image and old_image != self.image:
                # Удаляем старое изображение
                if old_image and old_image != 'default_images/default_foto.png':
                    self._delete_old_image(old_image)

        if self.image:
            self._compress_image()
        else:
            self.image = 'default_images/default_foto.png'

        super().save(*args, **kwargs)

    def _compress_image(self):
        """Метод для сжатия изображения без потери качества"""
        if not self.image:
            return
        # Открываем изображение с помощью Pillow
        img = Image.open(self.image)
        # Приводим формат к нижнему регистру для безопасного сравнения
        img_format = img.format.lower()
        # Проверяем формат изображения
        if img_format not in ['jpg', 'jpeg', 'png']:
            raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")
        # Если изображение PNG, сохраняем его с оптимизацией
        if img_format == 'png':
            img.save(self.image.path, format='PNG', optimize=True)
        else:
            # Для JPG и JPEG сохраняем с качеством 85%
            img.save(self.image.path, format='JPEG', quality=85, optimize=True)

    def _delete_old_image(self, old_image):
        if old_image and old_image != 'default_images/default_foto.png':
            old_image_path = old_image.path
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order']


class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dishes", verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to="dish_images/",
                              blank=True,
                              verbose_name="Фото блюда",
                              default='default_images/default_foto.png')
    is_available = models.BooleanField(default=True, verbose_name="Доступно ли блюдо?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    def save(self, *args, **kwargs):
        # Проверяем, есть ли изменения в изображении
        if self.pk:
            old_image = Dish.objects.get(pk=self.pk).image
            if old_image != self.image:
                if old_image and old_image != 'default_images/default_foto.png':
                    self._delete_old_image(old_image)

        # Сжимаем изображение перед сохранением
        if self.image:
            self._compress_image()
        else:
            self.image = 'default_images/default_foto.png'

        super().save(*args, **kwargs)

    def _compress_image(self):
        """Метод для сжатия изображения без потери качества"""
        if not self.image:
            return

        # Открываем изображение с помощью Pillow
        img = Image.open(self.image)

        # Приводим формат к нижнему регистру для безопасного сравнения
        img_format = img.format.lower()

        # Проверяем формат изображения
        if img_format not in ['jpg', 'jpeg', 'png']:
            raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")

        # Если изображение PNG, сохраняем его с оптимизацией
        if img_format == 'png':
            img.save(self.image.path, format='PNG', optimize=True)
        else:
            # Для JPG и JPEG сохраняем с качеством 85%
            img.save(self.image.path, format='JPEG', quality=85, optimize=True)

    def _delete_old_image(self, old_image):
        """Удаление старого изображения из хранилища"""
        if old_image and old_image != 'default_images/default_foto.png':
            old_image_path = old_image.path
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ['order']
        unique_together = ('category', 'name')


class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    image = models.ImageField(upload_to="restaurant_images/",
                              blank=True, verbose_name="Лого",
                              default='default_images/default_foto.png')

    def save(self, *args, **kwargs):
        if self.pk:
            old_image = Restaurant.objects.get(pk=self.pk).image

            if self.image and old_image != self.image:
                if old_image and old_image != 'default_images/default_foto.png':
                    self._delete_old_image(old_image)

        if self.image:
            self._compress_image()
        else:
            self.image = 'default_images/default_foto.png'

        super().save(*args, **kwargs)

    def _compress_image(self):
        if not self.image:
            return
        img = Image.open(self.image)
        img_format = img.format.lower()
        if img_format not in ['jpg', 'jpeg', 'png']:
            raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")
        if img_format == 'png':
            img.save(self.image.path, format='PNG', optimize=True)
        else:
            img.save(self.image.path, format='JPEG', quality=85, optimize=True)

    def _delete_old_image(self, old_image):
        if old_image and old_image != 'default_images/default_foto.png':
            old_image_path = old_image.path
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)

    def __str__(self):
        return self.name
