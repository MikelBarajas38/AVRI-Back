"""
URL mappings for the documents API.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from documents import views


router = DefaultRouter()

router.register('', views.DocumentViewSet, basename='document')

router.register(
    'saved',
    views.SavedDocumentViewSet,
    basename='saved-document'
)

router.register(
    'authored',
    views.AuthoredDocumentViewSet,
    basename='authored-document'
)

router.register(
    '',
    views.RepositoryDocumentViewSet,
    basename='repository-document'
)

app_name = 'documents'

urlpatterns = [
    path('', include(router.urls)),
]
