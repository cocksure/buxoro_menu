import os
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models


def process_image(image, upload_path, quality=60, max_size=(1024, 1024)):
    """Функция для обработки изображения: ресайз, конвертация в WebP, оптимизация."""
    try:
        img = Image.open(image)

        # Проверяем поддержку форматов
        if img.format.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
            raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")

        output = BytesIO()

        # Ограничение разрешения изображения
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)

        # Сохранение с оптимизацией
        img.save(output, format='WEBP', quality=quality, optimize=True)
        output.seek(0)

        # Сохраняем изображение в указанную папку
        new_image_name = os.path.splitext(image.name)[0] + '.webp'

        return new_image_name, ContentFile(output.read())

    except Exception as e:
        raise ValueError(f"Ошибка при обработке изображения: {e}")


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    image = models.ImageField(
        upload_to="category_images/",
        blank=True,
        verbose_name="Фото категории",
        default='default_images/default_foto.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])]
    )

    def save(self, *args, **kwargs):
        if self.image:
            new_name, new_file = process_image(self.image, "category_images/")

            if self.pk:
                old_instance = self.__class__.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    default_image_path = 'default_images/default_foto.png'
                    if old_instance.image.name != default_image_path:
                        old_instance.image.delete(save=False)

            self.image.save(new_name, new_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('display_order',)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dishes", verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(
        upload_to="dish_images/",
        blank=True,
        verbose_name="Фото блюда",
        default='default_images/default_foto.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])]
    )
    is_available = models.BooleanField(default=True, verbose_name="Доступно ли блюдо?")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    def save(self, *args, **kwargs):
        if self.image:
            new_name, new_file = process_image(self.image, "dish_images/")

            if self.pk:
                old_instance = self.__class__.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    default_image_path = 'default_images/default_foto.png'
                    if old_instance.image.name != default_image_path:
                        old_instance.image.delete(save=False)

            self.image.save(new_name, new_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        unique_together = ('category', 'name')
        ordering = ('display_order',)


class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название ресторана")
    image = models.ImageField(
        upload_to="restaurant_images/",
        blank=True,
        verbose_name="Лого",
        default='default_images/default_foto.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])]
    )

    def save(self, *args, **kwargs):
        if self.image:
            try:
                img = Image.open(self.image)

                if img.format.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
                    raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")

                if img.format.lower() != 'webp':
                    output = BytesIO()
                    img.save(output, format='WEBP', quality=85)
                    output.seek(0)

                    if self.pk:
                        old_instance = self.__class__.objects.get(pk=self.pk)
                        if old_instance.image and old_instance.image != self.image:
                            old_instance.image.delete(save=False)

                    self.image.save(
                        os.path.splitext(self.image.name)[0] + '.webp',
                        ContentFile(output.read()),
                        save=False
                    )

            except Exception as e:
                print(f"Ошибка при обработке изображения: {e}")
                raise

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"
