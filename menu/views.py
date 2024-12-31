from .models import Category, Dish, Restaurant
from django.shortcuts import render, redirect
from django.http import JsonResponse


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
        category = Category.objects.get(id=category_id)
        dishes = Dish.objects.filter(category=category, is_available=True)  # Добавил фильтр доступности

        dish_data = [
            {
                'id': dish.id,
                'name': dish.name,
                'description': dish.description,
                'price': str(dish.price),
                'image_url': dish.image.url if dish.image else None,
                'is_available': dish.is_available,
            }
            for dish in dishes
        ]
        return JsonResponse({'dishes': dish_data})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=404)


# views.py


def add_to_cart(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id, is_available=True)  # Проверяем доступность блюда
        cart = request.session.get('cart', {})

        if str(dish_id) in cart:
            cart[str(dish_id)]['quantity'] += 1
            message = f" {dish.name} увеличено!"
        else:
            cart[str(dish_id)] = {
                'name': dish.name,
                'price': str(dish.price),
                'quantity': 1
            }
            message = f"'{dish.name}' добавлено!"

        request.session['cart'] = cart

        total_quantity = sum(item['quantity'] for item in cart.values())
        return JsonResponse({'success': True, 'message': message, 'total_quantity': total_quantity})
    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Блюдо не найдено или недоступно'}, status=404)


def view_cart(request):
    cart = request.session.get('cart', {})

    if not cart:
        return render(request, 'view_cart.html', {'cart': {}, 'total_price': 0, 'message': 'Ваша корзина пуста!'})

    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

    context = {
        'cart': cart,
        'total_price': total_price,
    }

    return render(request, 'view_cart.html', context)


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
