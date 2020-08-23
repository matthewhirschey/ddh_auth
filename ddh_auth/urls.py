from django.contrib import admin
from django.urls import path
from userauth import views as user_auth_views

urlpatterns = [
    path('', user_auth_views.index, name='home'),
    path('auth/', user_auth_views.auth, name='auth'),
    path('login/', user_auth_views.Login.as_view(), name='login'),
    path('logout/', user_auth_views.logout, name='logout'),
    path('admin/', admin.site.urls),
]
