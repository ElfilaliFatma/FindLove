from django.urls import path

from user import views


urlpatterns = [
    path('', views.userProfile, name='userProfile'),

]
