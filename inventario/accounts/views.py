from accounts import views
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("login")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect("login")

    return render(request, "accounts/login.html")
