from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit


# middleware.py
class SaveUserIdMiddleware:
    """
    Если в GET-параметрах присутствует user_id, сохраняем его в сессии.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Сессия должна уже быть доступна, поэтому этот middleware
        # должен быть добавлен после SessionMiddleware
        user_id = request.GET.get('user_id')
        if user_id:
            request.session['user_id'] = user_id
            request.session.modified = True
        return self.get_response(request)


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not ratelimit(request, key='ip', rate='5/m', method='ALL'):
            return JsonResponse(
                {'error': 'Вы превысили лимит запросов. Пожалуйста, попробуйте позже.'},
                status=429
            )

        return self.get_response(request)
