from django.http import JsonResponse
from rest_framework import status


def success_response(data=None, message="ok"):
    if data is None:
        data = {}
    return JsonResponse({'code': 200, 'message': message, 'data': data}, status=status.HTTP_200_OK)


def bad_request_response(message="bad request"):
    return JsonResponse({'code': 400, 'detail': message}, status=status.HTTP_400_BAD_REQUEST)


def unauthorized_response(message="unauthorized"):
    return JsonResponse({'code': 401, 'detail': message}, status=status.HTTP_401_UNAUTHORIZED)


def not_found_response(message="not found"):
    return JsonResponse({'code': 404, 'detail': message}, status=status.HTTP_404_NOT_FOUND)


def internal_error_response(message="internal error"):
    return JsonResponse({'code': 500, 'detail': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
