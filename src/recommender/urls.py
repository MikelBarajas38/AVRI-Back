"""
URL mappings for the recommender API.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recommender import views

router = DefaultRouter()
router.register(
    '',
    views.DocumentRecommendationViewSet,
    basename='recommendations'
)

urlpatterns = [
    path(
        'profile/create/',
        views.CreateUserProfileView.as_view(),
        name='create'
    ),
    path(
        'profile/me/',
        views.ManageUserProfileView.as_view(),
        name='me'
    ),
    path('', include(router.urls)),
]
