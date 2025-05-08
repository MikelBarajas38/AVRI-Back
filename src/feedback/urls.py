"""
URL mappings for the feedback API.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from feedback import views


router = DefaultRouter()

router.register(
    '',
    views.SatisfactionSurveyResponseViewSet,
    basename='feedback'
)

app_name = 'feedback'

urlpatterns = [
    path('', include(router.urls)),
]
