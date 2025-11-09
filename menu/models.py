import os
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models


def process_image(image, quality=85, max_size=(1024, 1024)):
    """
    Универсальная функция для обработки изображения: ресайз, конвертация в WebP, оптимизация.

    Args:
        image: Файл изображения
        quality: Качество сжатия WebP (0-100)
        max_size: Максимальные размеры (ширина, высота)

    Returns:
        tuple: (новое_имя_файла, ContentFile)
    """
    try:
        img = Image.open(image)

        # Конвертация RGBA в RGB для WebP
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Проверяем поддержку форматов
        if img.format and img.format.lower() not in ['jpg', 'jpeg', 'png', 'webp', 'heic']:
            raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")

        # Ограничение разрешения изображения
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)

        # Сохранение с оптимизацией
        output = BytesIO()
        img.save(output, format='WEBP', quality=quality, optimize=True)
        output.seek(0)

        # Генерация нового имени файла
        new_image_name = os.path.splitext(os.path.basename(image.name))[0] + '.webp'

        return new_image_name, ContentFile(output.read())

    except Exception as e:
        raise ValueError(f"Ошибка при обработке изображения: {e}")


class ImageProcessingMixin(models.Model):
    """Базовый класс для моделей с обработкой изображений"""

    class Meta:
        abstract = True

    def _process_and_save_image(self, quality=85, max_size=(1024, 1024)):
        """Обработка и сохранение изображения с удалением старого"""
        if not self.image:
            return

        # Проверяем, изменилось ли изображение
        try:
            # Если объект уже существует в БД
            if self.pk:
                old_instance = self.__class__.objects.only('image').get(pk=self.pk)
                # Если изображение не изменилось, пропускаем обработку
                if old_instance.image == self.image:
                    return

                # Удаляем старое изображение (кроме дефолтного)
                default_image_path = 'default_images/default_foto.png'
                if old_instance.image and old_instance.image.name != default_image_path:
                    old_instance.image.delete(save=False)
        except self.__class__.DoesNotExist:
            pass

        # Обрабатываем новое изображение
        new_name, new_file = process_image(self.image, quality=quality, max_size=max_size)
        self.image.save(new_name, new_file, save=False)


class Category(ImageProcessingMixin):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения", db_index=True)
    image = models.ImageField(
        upload_to="category_images/",
        blank=True,
        verbose_name="Фото категории",
        default='default_images/default_foto.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])]
    )

    def save(self, *args, **kwargs):
        self._process_and_save_image(quality=85, max_size=(1024, 1024))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('display_order',)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        indexes = [
            models.Index(fields=['display_order'], name='category_order_idx'),
        ]


class Dish(ImageProcessingMixin):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dishes", verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название блюда", db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(
        upload_to="dish_images/",
        blank=True,
        verbose_name="Фото блюда",
        default='default_images/default_foto.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])]
    )
    is_available = models.BooleanField(default=True, verbose_name="Доступно ли блюдо?", db_index=True)
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения", db_index=True)

    def save(self, *args, **kwargs):
        self._process_and_save_image(quality=80, max_size=(1024, 1024))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        unique_together = ('category', 'name')
        ordering = ('display_order',)
        indexes = [
            models.Index(fields=['category', 'is_available', 'display_order'], name='dish_filtering_idx'),
            models.Index(fields=['is_available'], name='dish_available_idx'),
        ]


class Restaurant(ImageProcessingMixin):
    name = models.CharField(max_length=100, verbose_name="Название ресторана", unique=True)
    image = models.ImageField(
        upload_to="restaurant_images/",
        blank=True,
        verbose_name="Лого",
        default='default_images/default_foto.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])]
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание ресторана")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    telegram = models.URLField(blank=True, null=True, verbose_name="Telegram")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def save(self, *args, **kwargs):
        self._process_and_save_image(quality=90, max_size=(800, 800))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"
