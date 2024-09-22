from django.urls import path

from apps.api.views import status, user, token, password

urlpatterns = [
    # Authentication
    path('token', token.TokenManagement.as_view(), name='token'),

    # User
    path('users', user.UserManagement.as_view()),
    path('users/<uuid:user_id>', user.UserDetail.as_view()),
    path('users/me', user.UserMe.as_view()),

    # Password Recovery
    path('password/recovery', password.PasswordRecoveryManagement.as_view(), name='password-recovery'),
    path('password/change', password.PasswordChangeManagement.as_view(), name='password-change'),

    # Status
    path("status", status.StatusManagement.as_view(), name='status'),
]
