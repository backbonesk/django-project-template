from django.urls import path

from apps.api.views import status, user, auth


urlpatterns = [
    # Authentication
    path('auth', auth.UserAuth.as_view(), name='auth-token-login'),
    path('logout', auth.LogoutManager.as_view(), name='auth-token-logout'),

    # User
    path('users', user.UserManagement.as_view()),
    path('users/<uuid:user_id>', user.UserDetail.as_view()),
    path('users/me', user.UserMe.as_view()),

    # Status
    path("status", status.StatusManagement.as_view(), name='status'),
]
