"""
URL mappings for the user API.
"""

from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path(
        'create-anonymous/',
        views.CreateAnonymousUserView.as_view(),
        name='create-anonymous'
    ),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path(
        'token-anonymous/',
        views.CreateAnonymousTokenView.as_view(),
        name='token-anonymous'
    ),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('list/', views.ListUsersView.as_view(), name='list')
]
