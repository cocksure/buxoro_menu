from .models import Category, Dish, Restaurant
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect


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
        items_per_page = 10  # Количество блюд на страницу

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


# views.py


def add_to_cart(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id, is_available=True)  # Проверяем доступность блюда
        cart = request.session.get('cart', {})

        # Добавляем блюдо в корзину, если его нет
        if str(dish_id) not in cart:
            cart[str(dish_id)] = {
                'name': dish.name,
                'price': str(dish.price),
                'quantity': 1  # Первоначальное количество
            }
            message = f"'{dish.name}' добавлено в корзину!"
        else:
            message = f"{dish.name} уже в корзине!"

        request.session['cart'] = cart  # Сохраняем корзину в сессии

        # Считаем общее количество товаров в корзине
        total_quantity = sum(item['quantity'] for item in cart.values())
        return JsonResponse({'success': True, 'message': message, 'total_quantity': total_quantity})

    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Блюдо не найдено или недоступно'}, status=404)


def view_cart(request):
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})

    # Если корзина пуста, отображаем соответствующее сообщение
    if not cart:
        return render(request, 'view_cart.html', {'cart': {}, 'total_price': 0, 'message': 'Ваша корзина пуста!'})

    # Рассчитываем общую сумму корзины
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

    # Отправляем данные корзины и общей суммы в шаблон
    context = {
        'cart': cart,
        'total_price': total_price,
    }
    return render(request, 'view_cart.html', context)


def update_cart(request):
    try:
        # Получаем данные из запроса
        dish_id = request.POST.get('dish_id')
        quantity = int(request.POST.get('quantity'))

        # Получаем корзину из сессии
        cart = request.session.get('cart', {})

        # Проверяем, есть ли блюдо в корзине
        if dish_id in cart:
            cart[dish_id]['quantity'] = quantity  # Обновляем количество

        # Пересчитываем общую сумму
        total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

        # Сохраняем обновленную корзину
        request.session['cart'] = cart

        # Возвращаем обновленную общую сумму
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
