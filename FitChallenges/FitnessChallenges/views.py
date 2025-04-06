from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Posts, Challenges
from django.views.decorators.csrf import csrf_exempt
import json
import random
from .login import users_login
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from .onboard import users_onboard
from django.db.models import Q
import logging

logger = logging.getLogger('django')


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh["user_id"] = user.id  # ✅ Add this line
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Create your views here.
def get_users(request):
    users = User.objects.filter(verified="True").values('id', 'first_name', 'last_name', 'user_name', 'gender', 'email_address', 'created_at', 'phone_number', 'height', 'weight', 'smoke_habits', 'alcohol_habits')
    user_list = list(users)
    return JsonResponse(
        user_list, safe=False
    )
    

def home(request):
    posts = Posts.objects.all().order_by('created_at')  

    # Build response with full media URLs
    post_list = []
    for post in posts:
        post_list.append({
            "id": post.id,
            "caption": post.caption,
            "username": post.user.user_name,
            "created_at": post.created_at
        })

    return JsonResponse(post_list, safe=False)

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            token_str = request.POST.get("access_token")
            access_token = AccessToken(token_str)
            u_id = access_token['user_id'] 
            user = User.objects.get(id=u_id)        
            
            # Form data (multipart/form-data in Postman)
            caption = request.POST.get('caption')
            # media_image_video = request.FILES.get('media_image_video')
            
            post = Posts.objects.create(
                caption=caption,
                # profile_image=media_image_video,
                user = user
            )
            
            print("FILES:", request.FILES)

            return JsonResponse({
                "success": True,
                # "message": request.FILES.get('media_image_video'),
                "post_id": post.id
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "Error while creating post",
                "error": str(e)
            }, status=400)

    return JsonResponse({"message": "Only POST method allowed"}, status=405)


@csrf_exempt
def otp_verification(request):
    otp_details = json.loads(request.body)
    if request.method == "POST":
        try: 
            token_str = otp_details.get("access_token")
            user_otp = otp_details.get("entered_otp")
            
            access_token = AccessToken(token_str)

            # Extract the user_id from payload
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            db_otp = user.verified
            
            if user_otp == db_otp:
                User.objects.filter(id=user_id).update(verified="True")
                return JsonResponse({
                    "success": True
                })
            else:
                return JsonResponse({
                    "success": False,
                    "message": "OTP is invalid"
                })
        except (TokenError, InvalidToken) as e:
            return JsonResponse({
                "success": False,
                "message": "Token is invalid or expired"
            }, status=401)


@csrf_exempt
def user_signup(request):
    if request.method == "POST":
        otp_num = random.randint(1000, 9999)
        user_data = json.loads(request.body)
        try:
            email = User.objects.get(email_address=user_data.get("email"))
            if email:
                return JsonResponse(
                    {"success": False,
                        "message": "Email Address Already Exists"}
                )
        except User.DoesNotExist as e:
            pass
        
        try:
            u_name = User.objects.get(user_name=user_data.get("username"))
            if u_name:
                return JsonResponse(
                    {"success": False,
                        "message": "Username Already Exists"}
                )
        except User.DoesNotExist as e:
            pass
    
        except User.MultipleObjectsReturned as e:
            return JsonResponse(
                    {"success": False,
                        "message": "Username Already Exists"}
                )
        
        new_user = User.objects.create(
            first_name = user_data.get("first_name"),
            last_name = user_data.get("last_name"),
            user_name = user_data.get("username"),
            email_address = user_data.get("email"),
            password = user_data.get("password"),
            phone_number = user_data.get("phone"),
            verified = str(otp_num)
        )
        
        user = User.objects.get(email_address=user_data.get("email"))
        tokens = get_tokens_for_user(user)
        subject = "🎉 Welcome to FitLinked!"
        html_content = f"""
            <html>
                <body>
                    <p>Hi {user_data.get("user_name")},</p>
                    <p>Thank you for signing up for <strong>FitLinked</strong>. Get ready to challenge and level up your wellness journey!</p>
                    <p><strong style="font-size: 24px;">Your OTP is: {otp_num}</strong></p>
                    <p>Cheers,<br>The FitLinked Team</p>
                </body>
            </html>
        """
        
        # Plain text fallback
        text_content = strip_tags(html_content)

        # Send email
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [user_data.get("email")],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return JsonResponse(
            {"success": True,
                "user_id": user.id,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"]}
        )
         


@csrf_exempt
def user_login(request):
    return users_login(request)

@csrf_exempt
def user_onboard(request):
    return users_onboard(request)




@csrf_exempt
def post_challenges(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            access_token = data.get('access_token')
            challenge_name = data.get('challenge_name')
            description = data.get('description')
            user_invitation = data.get('user_invitation')

            if not access_token:
                return JsonResponse({'error': 'Access token is required'}, status=400)
            if not challenge_name or not user_invitation:
                return JsonResponse({'error': 'Challenge name and user_invitation are required'}, status=400)

            # Decode token to get user_id
            token = AccessToken(access_token)
            user_id = token['user_id']

            # Get the user from DB
            user = User.objects.get(id=user_id)

            # Save the challenge
            challenge = Challenges.objects.create(
                user=user,
                challenge_name=challenge_name,
                description=description,
                user_invitation=user_invitation
            )

            return JsonResponse({
                'message': 'Challenge created successfully',
                'challenge_id': challenge.id
            }, status=201)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def get_chanellenges(request):
    if request.method == 'POST':
        try:
            # Get access token from POST body or form data
            token_str = request.POST.get("access_token") or json.loads(request.body).get("access_token")
            if not token_str:
                return JsonResponse({"error": "Access token missing"}, status=400)

            # Decode token to get user ID
            access_token = AccessToken(token_str)
            u_id = access_token['user_id']
            user = User.objects.get(id=u_id)

            # Fetch challenges created by user or invited via email
            challenges = Challenges.objects.filter(
                Q(user=user) | Q(user_invitation=user.email_address)
            ).order_by('-created_at')

            result = []
            for ch in challenges:
                # Get creator user_name
                creator_name = ch.user.user_name if ch.user else None

                # Fix: lookup friend by email_address (case-insensitive)
                email = ch.user_invitation.strip().lower()
                friend = User.objects.filter(email_address__iexact=email).first()
                friend_name = friend.user_name if friend else None

                result.append({
                    'id': ch.id,
                    'challenge_name': ch.challenge_name,
                    'description': ch.description,
                    'invited_email': ch.user_invitation,
                    'friend_name': friend_name,
                    'creator_user_id': ch.user_id,
                    'creator_name': creator_name,
                    'created_at': ch.created_at,
                    'challenge_completed': ch.challenge_completed
                })

            return JsonResponse(result, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
