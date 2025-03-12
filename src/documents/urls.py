"""
URL mappings for the documents API.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from documents import views


router = DefaultRouter()
router.register('documents', views.DocumentViewSet)

app_name = 'documents'

urlpatterns = [
    path('', include(router.urls)),
]
