import os
from PIL import Image
from django.db import models
from django.core.validators import FileExtensionValidator
from io import BytesIO
from django.core.files.base import ContentFile



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
            try:
                # Открываем изображение
                img = Image.open(self.image)

                # Проверяем формат изображения
                if img.format.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
                    raise ValueError(f"Неподдерживаемый формат изображения: {img.format}")

                # Если изображение уже в формате WebP, пропускаем конвертацию
                if img.format.lower() != 'webp':
                    # Конвертируем изображение в WebP
                    output = BytesIO()
                    img.save(output, format='WEBP', quality=85)  # Качество 85%
                    output.seek(0)

                    # Удаляем старое изображение, если оно было
                    if self.pk:
                        old_instance = self.__class__.objects.get(pk=self.pk)
                        if old_instance.image and old_instance.image != self.image:
                            old_instance.image.delete(save=False)

                    # Сохраняем новое изображение
                    self.image.save(
                        os.path.splitext(self.image.name)[0] + '.webp',  # Меняем расширение на .webp
                        ContentFile(output.read()),
                        save=False
                    )

            except Exception as e:
                # Логируем ошибку, если что-то пошло не так
                print(f"Ошибка при обработке изображения: {e}")
                raise

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
                            # Проверяем, не является ли старое изображение файлом по умолчанию
                            default_image_path = os.path.join('default_images', 'default_foto.png')
                            if old_instance.image.name != default_image_path:
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


#
