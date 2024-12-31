from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit


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
