import datetime
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import COMPATIBILITY, Notification, UserProfile

from datetime import datetime
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import UserProfile

COMPATIBILITY = {
    "Aries": ["Leo", "Sagittarius", "Gemini"],
    "Taurus": ["Virgo", "Capricorn", "Cancer"],
  
}

@csrf_exempt
@require_POST
def register_user(request):
    try:
        data = json.loads(request.body)
        
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        birthdate_str = data.get('birthdate')
        zodiac = data.get('zodiac')
        gender = data.get('gender')

        if not (first_name and last_name and birthdate_str and zodiac and gender):
            return HttpResponseBadRequest("Missing required fields.")
        
       
        if UserProfile.objects.filter(first_name=first_name, last_name=last_name).exists():
            return HttpResponseBadRequest(f"A user with the name {first_name} {last_name} already exists.")

      
        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponseBadRequest("Invalid birthdate format. Use YYYY-MM-DD.")
        
    
        profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            zodiac=zodiac,
            gender=gender
        )
        
        return JsonResponse({
            "message": "User registered successfully!",
            "user_id": profile.id
        })

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

    
@csrf_exempt
@require_POST
def get_compatible_users(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')

        if not user_id:
            return HttpResponseBadRequest("user_id is required.")
        
        
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return HttpResponseBadRequest("User does not exist.")
        
        
        compatible_zodiacs = COMPATIBILITY.get(user.zodiac, [])
        
        
        compatible_users = UserProfile.objects.filter(zodiac__in=compatible_zodiacs)
        
        
        if user.gender == "Female":
            compatible_users = compatible_users.filter(gender="Male")
        elif user.gender == "Male":
            compatible_users = compatible_users.filter(gender="Female")
        
        
        compatible_list = [
            {
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "birthdate": u.birthdate.strftime("%Y-%m-%d") if u.birthdate else None,
                "zodiac": u.zodiac,
                "gender": u.gender
            }
            for u in compatible_users
        ]
        
        return JsonResponse({
            "message": "Compatible users found!",
            "compatible_users": compatible_list
        })

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")
 
@csrf_exempt
@require_POST
def select_compatible_user(request):
    try:
        data = json.loads(request.body)
        user_id, selected_user_id = data.get('user_id'), data.get('selected_user_id')

        if not user_id or not selected_user_id:
            return HttpResponseBadRequest("Both user_id and selected_user_id are required.")

        user, selected_user = UserProfile.objects.get(id=user_id), UserProfile.objects.get(id=selected_user_id)

        if selected_user.selected_match or selected_user.match_accepted:
            return HttpResponseBadRequest(f"{selected_user.first_name} is already matched.")
        if user.selected_match:
            return HttpResponseBadRequest(f"{user.first_name} has already selected someone.")

        user.selected_match = selected_user
        user.save()

        Notification.objects.create(receiver=selected_user, sender=user, message=f"{user.first_name} selected you!")
        return JsonResponse({"message": f"{user.first_name} selected {selected_user.first_name}."})
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")

@csrf_exempt
@require_POST
def accept_match(request):
    try:
        data = json.loads(request.body)
        user_id, match_id, accept = data.get('user_id'), data.get('match_id'), data.get('accept')

        if not user_id or not match_id:
            return HttpResponseBadRequest("Both user_id and match_id are required.")

        user = UserProfile.objects.get(id=user_id)
        match = UserProfile.objects.get(id=match_id)

        if accept:
            # Accept the match: Update 'match_accepted' to True for both users
            user.match_accepted = True
            match.match_accepted = True
            user.save()
            match.save()

            message = f"{match.first_name} accepted your match!"
        else:
            # Reject the match: Update 'match_accepted' to False for both users
            user.match_accepted = False
            match.match_accepted = False
            user.save()
            match.save()

            message = f"{match.first_name} rejected your match."

        # Create a notification for the user
        Notification.objects.create(receiver=user, sender=match, message=message)
        return JsonResponse({"message": message})

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")



@csrf_exempt
def get_notifications(request, user_id):
    try:
        notifications = Notification.objects.filter(receiver_id=user_id, is_read=False)
        return JsonResponse({"notifications": [{"id": n.id, "message": n.message} for n in notifications]})
    except UserProfile.DoesNotExist:
        return HttpResponseBadRequest("User does not exist.")

@csrf_exempt
def get_possible_matches(request, user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
        
   
        unmatched_users = UserProfile.objects.exclude(matches=user).exclude(selected_match__isnull=False)
        if user.gender == "Female":
            unmatched_users = unmatched_users.filter(gender="Male")
        elif user.gender == "Male":
            unmatched_users = unmatched_users.filter(gender="Female")
        
        return JsonResponse({"matches": list(unmatched_users.values("id", "first_name", "last_name"))})
    except UserProfile.DoesNotExist:
        return HttpResponseBadRequest("User does not exist.")



from django.http import JsonResponse
from user.models import UserProfile

def get_all_matches(request):
    matches = []
    
    all_users = UserProfile.objects.all()

    for user in all_users:
        if user.selected_match:
            status = "Pending"
            if user.match_accepted is True:
                status = "Accepted"
            elif user.match_accepted is False:
                status = "Rejected"
            
            matches.append({
                "user_id": user.id,
                "user_name": f"{user.first_name} {user.last_name}",
                "selected_match_id": user.selected_match.id,
                "selected_match_name": f"{user.selected_match.first_name} {user.selected_match.last_name}",
                "status": status
            })
    
    return JsonResponse({"matches": matches})




@csrf_exempt
def get_pending_requests(request, user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
        pending_requests = user.get_pending_requests()
        return JsonResponse({
            "pending_requests": [
                {"id": req.id, "first_name": req.first_name, "last_name": req.last_name, "zodiac": req.zodiac}
                for req in pending_requests
            ]
        })
    except UserProfile.DoesNotExist:
        return HttpResponseBadRequest("User does not exist.")
