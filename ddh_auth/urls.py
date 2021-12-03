from django.contrib import admin
from django.urls import path
from userauth import views as user_auth_views

urlpatterns = [
    path('', user_auth_views.index, name='home'),
    path('auth/', user_auth_views.auth, name='auth'),
    path('webhook/', user_auth_views.webhook, name='webhook'),
    path('login/', user_auth_views.Login.as_view(), name='login'),
    path('accounts/reset/<uidb64>/<token>/',  user_auth_views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', user_auth_views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('logout/', user_auth_views.logout, name='logout'),
    path('admin/', admin.site.urls),
]
