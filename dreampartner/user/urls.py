from django.urls import path
from user import views

urlpatterns = [
    path('zodiac-compatibility/', views.zodiac_compatibility_view, name='zodiac_compatibility'),
    path('select-compatible/', views.select_compatible_user, name='select_compatible_user'),
    path('accept-match/', views.accept_match, name='accept_match'), 
    path('get-notifications/<int:user_id>/', views.get_notifications, name='get_notifications'),
    path('possible-matches/<int:user_id>/', views.get_possible_matches, name='get_possible_matches'),
    path('get-matches/', views.get_all_matches, name='get_all_matches'),  
    path('pending-requests/<int:user_id>/', views.get_pending_requests, name='pending_requests'),  
]
