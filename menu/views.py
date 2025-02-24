from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .models import Category, Dish, Restaurant


def menu_view(request):
    restaurant = Restaurant.objects.first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'restaurant': restaurant if restaurant else None,
    }
    return render(request, 'menu.html', context)


def load_dishes(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id)
        dishes = Dish.objects.filter(category=category, is_available=True)  # Фильтруем блюда

        # Параметры пагинации
        page_number = request.GET.get('page', 1)  # Текущая страница (по умолчанию 1)
        items_per_page = 12  # Количество блюд на страницу

        paginator = Paginator(dishes, items_per_page)  # Создаем пагинатор
        page_obj = paginator.get_page(page_number)  # Получаем страницу

        dish_data = [
            {
                'id': dish.id,
                'name': dish.name,
                'description': dish.description,
                'price': str(dish.price),
                'image_url': dish.image.url if dish.image else None,
                'is_available': dish.is_available,
            }
            for dish in page_obj
        ]

        # Возвращаем информацию о блюдах и пагинации
        return JsonResponse({
            'dishes': dish_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

    except Category.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=404)


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
    try:
        dish_id = str(request.POST.get('dish_id'))
        quantity = int(request.POST.get('quantity'))

        cart = request.session.get('cart', {})

        if dish_id in cart:
            cart[dish_id]['quantity'] = quantity
        else:
            return JsonResponse({'success': False, 'message': f'Блюдо с id {dish_id} не найдено в корзине.'})

        total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
        request.session['cart'] = cart

        return JsonResponse({'success': True, 'total_price': total_price})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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
            print("Cart after adding: ", cart)  # Логируем корзину

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
