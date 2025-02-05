from django.shortcuts import render

# Create your views here.



def userProfile(request):
    return render(request,"user.html")