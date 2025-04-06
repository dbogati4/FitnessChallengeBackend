from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
import random
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@csrf_exempt
def users_login(request):
    if request.method == "POST":
        user_data = json.loads(request.body)
        username_or_email = user_data.get("identifier")

        user_login_id = None

        try:
            # Try by email first
            user_login_id = User.objects.get(email_address=username_or_email)
        except User.DoesNotExist:
            try:
                # Then try by username
                user_login_id = User.objects.get(user_name=username_or_email)
            except User.DoesNotExist:
                user_login_id = None

        if not user_login_id:
            return JsonResponse({
                "success": False,
                "message": "User does not exist"
            }, status=404)
        
        if user_login_id.password == user_data.get("password"):
            tokens = get_tokens_for_user(user_login_id)
            return JsonResponse(
                {"success": True,
                    "user_id": "Login Success",
                "access_token": tokens['access'],
                "refresh_token": tokens['refresh']
                    }
            )
        else:
            return JsonResponse(
                {"success": False,
                    "message": "Password Mismatch"}
            )
         

