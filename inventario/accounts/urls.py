#urls for accounts app
from django.urls import path
# urls for auth views
from django.contrib.auth import views as auth_views
#viwews for accounts app
from . import views

app_name = 'accounts'
# URL patterns for the accounts app
urlpatterns = [
    path(
        'login/', 
        auth_views.LoginView.as_view(template_name='login'), 
        name='login'
    ),
    path(
        'logout/', 
        auth_views.LogoutView.as_view(), 
         name='logout'
         ),
]