from django.urls import path

from apps.api.views import user, auth, password


urlpatterns = [
    # Authentication
    path('auth', auth.UserAuth.as_view(), name='auth-token-login'),
    path('logout', auth.LogoutManager.as_view(), name='auth-token-logout'),

    # User
    path('users', user.UserManagement.as_view()),
    path('users/<uuid:user_id>', user.UserDetail.as_view()),
    path('users/me', user.UserMe.as_view()),

    # Password Recovery
    path('password/recovery', password.PasswordRecoveryManagement.as_view(), name='password-recovery'),
    path('password/change', password.ChangePasswordManagement.as_view(), name='password-change'),
]
