from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition
import os
import time

from .models import Category, Dish, Restaurant


def serve_menu_pdf(request):
    """Отдача PDF меню с долгосрочным кешированием в браузере"""
    # Путь к PDF файлу
    pdf_path = os.path.join(settings.BASE_DIR, 'static', 'menu', 'menu.pdf')

    # Проверяем существование файла
    if not os.path.exists(pdf_path):
        raise Http404("PDF меню не найдено")

    # Открываем файл и создаем ответ
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

    # Устанавливаем заголовки для долгосрочного кеширования
    # Cache-Control: кешировать на 30 дней (2592000 секунд)
    response['Cache-Control'] = 'public, max-age=2592000, immutable'

    # ETag для проверки изменений файла (используем время модификации)
    file_mtime = os.path.getmtime(pdf_path)
    etag = f'"{int(file_mtime)}"'
    response['ETag'] = etag

    # Expires заголовок (дополнительно для старых браузеров)
    expires_time = time.time() + 2592000  # 30 дней
    response['Expires'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(expires_time))

    # Content-Disposition: открыть в браузере (не скачивать)
    response['Content-Disposition'] = 'inline; filename="menu.pdf"'

    return response


def menu_view(request):
    """Главная страница меню с категориями и информацией о ресторане"""
    restaurant = Restaurant.objects.filter(is_active=True).first()
    categories = Category.objects.all().order_by('display_order')

    # Проверяем секретный ключ для режима редактирования
    edit_key = request.GET.get('edit', '')

    # 🔹 Минимальный фикс для теста на телефоне
    is_edit_mode = (edit_key == settings.EDIT_SECRET_KEY)
    # Если хочешь быстро проверить, всегда True для любого ?edit
    # is_edit_mode = bool(edit_key)

    context = {
        'categories': categories,
        'restaurant': restaurant,
        'is_edit_mode': is_edit_mode,
    }
    return render(request, 'menu.html', context)


def load_dishes(request, category_id):
    """Загрузка блюд по категории с пагинацией и кешированием"""
    try:
        # Проверяем существование категории
        category = get_object_or_404(Category, id=category_id)

        # Параметры пагинации
        page_number = int(request.GET.get('page', 1))
        items_per_page = 15

        # Генерируем ключ для кеша
        cache_key = f'dishes_cat_{category_id}_page_{page_number}'

        # Пробуем получить из кеша
        cached_response = cache.get(cache_key)
        if cached_response:
            return JsonResponse(cached_response)

        # Если нет в кеше, делаем запрос к БД с оптимизацией
        dishes = Dish.objects.filter(
            category=category,
            is_available=True
        ).only('id', 'name', 'description', 'price', 'image').order_by('display_order')

        # Создаем пагинатор
        paginator = Paginator(dishes, items_per_page)
        page_obj = paginator.get_page(page_number)

        # Формируем данные
        dish_data = [
            {
                'id': dish.id,
                'name': dish.name,
                'description': dish.description or '',
                'price': str(dish.price),
                'image_url': dish.image.url if dish.image else None,
                'is_available': dish.is_available,
            }
            for dish in page_obj
        ]

        # Формируем ответ
        response_data = {
            'dishes': dish_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        }

        # Кешируем на 5 минут
        cache.set(cache_key, response_data, 60 * 5)

        return JsonResponse(response_data)

    except Category.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Неверный формат параметров'}, status=400)


def add_to_cart(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id, is_available=True)
        cart = request.session.get('cart', {})

        if str(dish_id) not in cart:
            cart[str(dish_id)] = {
                'name': dish.name,
                'price': str(dish.price),
                'quantity': 1
            }
            message = f"'{dish.name}' добавлено в корзину!"
        else:
            message = f"{dish.name} уже в корзине!"

        request.session['cart'] = cart
        request.session.modified = True  # Добавляем эту строку

        total_quantity = sum(item['quantity'] for item in cart.values())
        return JsonResponse({'success': True, 'message': message, 'total_quantity': total_quantity})

    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Блюдо не найдено или недоступно'}, status=404)


def view_cart(request):
    cart = request.session.get('cart', {})

    total_price = 0
    for item in cart.values():
        total_price += float(item['price']) * item['quantity']

    context = {
        'cart': cart,
        'total_price': total_price,
    }

    return render(request, 'view_cart.html', context)


def update_cart(request):
    """Обновление количества блюда в корзине с валидацией"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        dish_id = str(request.POST.get('dish_id'))
        quantity = int(request.POST.get('quantity', 0))

        # Валидация количества
        if quantity < 1:
            return JsonResponse({'success': False, 'message': 'Количество должно быть больше 0'}, status=400)
        if quantity > 99:
            return JsonResponse({'success': False, 'message': 'Максимальное количество - 99'}, status=400)

        cart = request.session.get('cart', {})

        if dish_id in cart:
            cart[dish_id]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
        else:
            return JsonResponse({'success': False, 'message': f'Блюдо с id {dish_id} не найдено в корзине.'}, status=404)

        total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

        return JsonResponse({'success': True, 'total_price': total_price})
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Ошибка сервера'}, status=500)

def remove_from_cart(request, dish_id):
    cart = request.session.get('cart', {})

    if str(dish_id) in cart:
        del cart[str(dish_id)]
        request.session['cart'] = cart
        return redirect('view_cart')
    else:
        return JsonResponse({'error': 'Товар не найден в корзине'}, status=404)


def get_cart(request):
    cart = request.session.get('cart', {})

    total_quantity = sum(item['quantity'] for item in cart.values())

    return JsonResponse({'total_quantity': total_quantity})


# ------------------------- API views -------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CategorySerializer, DishSerializer, RestaurantSerializer


class RestaurantListView(APIView):

    def get(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListView(APIView):

    def get(self, request):
        categories = Category.objects.all().order_by('display_order')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DishListView(APIView):

    def get(self, request, category_id=None):
        items_per_page = int(request.GET.get('per_page', 20))  # Кол-во блюд на страницу
        page_number = int(request.GET.get('page', 1))  # Текущая страница

        if category_id:
            category = get_object_or_404(Category, id=category_id)
            dishes = Dish.objects.filter(category=category, is_available=True).order_by('display_order')
        else:
            dishes = Dish.objects.filter(is_available=True).order_by('display_order')

        # Пагинация
        paginator = Paginator(dishes, items_per_page)
        page_obj = paginator.get_page(page_number)

        serializer = DishSerializer(page_obj, many=True)
        return Response({
            'dishes': serializer.data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        }, status=status.HTTP_200_OK)


class CartView(APIView):

    def get(self, request):
        cart = request.session.get('cart', {})
        total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
        return Response({
            'cart': cart,
            'total_price': total_price,
            'message': 'Корзина пуста.' if not cart else 'Корзина содержит товары.'
        }, status=status.HTTP_200_OK)

    def post(self, request):
        dish_id = request.data.get('dish_id')
        try:
            dish = Dish.objects.get(id=dish_id, is_available=True)
            cart = request.session.get('cart', {})

            if str(dish_id) not in cart:
                cart[str(dish_id)] = {
                    'name': dish.name,
                    'price': str(dish.price),
                    'quantity': 1
                }
                message = f"'{dish.name}' добавлено в корзину!"
            else:
                message = f"'{dish.name}' уже в корзине!"

            request.session['cart'] = cart
            request.session.modified = True

            total_quantity = sum(item['quantity'] for item in cart.values())
            return Response({'message': message, 'total_quantity': total_quantity}, status=status.HTTP_200_OK)
        except Dish.DoesNotExist:
            return Response({'error': 'Блюдо не найдено или недоступно'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        dish_id = request.data.get('dish_id')
        quantity = request.data.get('quantity', 1)

        try:
            cart = request.session.get('cart', {})

            if str(dish_id) in cart:
                cart[str(dish_id)]['quantity'] = int(quantity)
                request.session['cart'] = cart
                total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
                return Response({'message': 'Количество обновлено', 'total_price': total_price},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        dish_id = request.data.get('dish_id')

        try:
            cart = request.session.get('cart', {})

            if str(dish_id) in cart:
                del cart[str(dish_id)]
                request.session['cart'] = cart
                total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
                return Response({'message': 'Блюдо удалено из корзины', 'total_price': total_price},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BulkDataAPIView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        dishes = Dish.objects.all()

        data = {
            "categories": CategorySerializer(categories, many=True).data,
            "dishes": DishSerializer(dishes, many=True).data,
        }
        return Response(data)


def update_dish(request):
    """Обновление данных блюда (только при наличии секретного ключа)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    # Проверяем секретный ключ
    edit_key = request.POST.get('edit_key', '')
    if edit_key != settings.EDIT_SECRET_KEY:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    try:
        dish_id = request.POST.get('dish_id')
        dish = get_object_or_404(Dish, id=dish_id)

        # Обновляем поля
        dish.name = request.POST.get('name', dish.name)
        dish.description = request.POST.get('description', dish.description)
        dish.price = request.POST.get('price', dish.price)
        dish.is_available = request.POST.get('is_available') == 'on'

        # Обновляем изображение, если загружено новое
        if 'image' in request.FILES:
            dish.image = request.FILES['image']

        dish.save()

        # Очищаем кеш для категории этого блюда
        category_id = dish.category.id
        cache_pattern = f'dishes_cat_{category_id}_page_*'
        # Удаляем все кеши для этой категории
        for i in range(1, 100):  # Предполагаем максимум 100 страниц
            cache.delete(f'dishes_cat_{category_id}_page_{i}')

        return JsonResponse({
            'success': True,
            'message': f'Блюдо "{dish.name}" успешно обновлено!',
            'dish': {
                'id': dish.id,
                'name': dish.name,
                'description': dish.description,
                'price': str(dish.price),
                'image_url': dish.image.url if dish.image else None,
                'is_available': dish.is_available,
            }
        })

    except Exception as e:
        return JsonResponse({'error': f'Ошибка при обновлении: {str(e)}'}, status=500)
