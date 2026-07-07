import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai import get_bot_response
from .models import ChatLog


@csrf_exempt
def chat_api_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    response, intent = get_bot_response(message)

    ChatLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        message=message,
        response=response,
        intent=intent,
    )

    return JsonResponse({'response': response, 'intent': intent})
