from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
import random
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from decimal import Decimal


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['user_id'] = user.id  # ✅ custom claim in refresh

    # Also add to access token
    access_token = refresh.access_token
    access_token['user_id'] = user.id  # ✅ now available in frontend/backend

    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }


@csrf_exempt
def users_onboard(request):

    onboard_details = json.loads(request.body)
    if request.method == "POST":
        token_str = onboard_details.get("access_token")
        
        access_token = AccessToken(token_str)

        # Extract the user_id from payload
        user_id = access_token['user_id']
        
        # 🔄 Update 3 fields using user_id
        User.objects.filter(id=user_id).update(
            gender=onboard_details.get("gender"), 
            height=Decimal(onboard_details.get("height")),
            weight=Decimal(onboard_details.get("weight")),
            smoke_habits=onboard_details.get("smoking"),
            alcohol_habits=onboard_details.get("alcohol"),
            dob=onboard_details.get("dob")
        )

        return JsonResponse({
            "success": True,
            "message": "User onboarded successfully"
        })


        

