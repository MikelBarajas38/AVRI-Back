"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

from django.urls import path
import json
from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse
from django.urls.resolvers import URLPattern
from core.statistics import (
    get_user_field_of_study_stats,
    get_most_consulted_documents_stats,
    get_most_consulted_authors_stats,
    get_document_keywords_stats,
    get_user_education_level_stats,
    get_user_activity_status_stats,
    get_chats_over_time_stats,
)
from core.export_stats import (
    export_user_field_of_study_csv,
    export_user_education_level_csv,
    export_user_activity_status_csv,
    export_most_consulted_documents_csv,
    export_most_consulted_authors_csv,
    export_document_keywords_csv,
    export_chats_over_time_csv,
)


class UserAdmin(BaseUserAdmin):
    """
    Define the admin pages for users.
    """
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_author'
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
        (_('Personal info'), {'fields': ('name', 'first_name', 'last_name')}),
        (
            _('Education info'),
            {
                'fields': (
                    'education_level',
                    'field_of_study',
                )
            }
        ),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    def changelist_view(
            self, request: HttpRequest,
            extra_context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Customize the changelist view to include statistics in
        the admin template context.
        """
        extra_context = extra_context or {}
        extra_context['user_stats_data'] = json.dumps(
            get_user_field_of_study_stats())
        extra_context['user_edu_level_data'] = json.dumps(
            get_user_education_level_stats())
        extra_context['user_activity_status_data'] = json.dumps(
            get_user_activity_status_stats())
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self) -> list[URLPattern]:
        """
        Add custom admin URLs for exporting statistics to CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export-field-of-study-csv/', self.admin_site.admin_view(
                export_user_field_of_study_csv),
                name='user_field_of_study_stats_export'),
            path('export-education-level-csv/', self.admin_site.admin_view(
                export_user_education_level_csv),
                name='user_education_level_stats_export'),
            path('export-activity-status-csv/', self.admin_site.admin_view(
                export_user_activity_status_csv),
                name='user_activity_status_stats_export'),
        ]
        return custom_urls + urls


class DocumentAdmin(admin.ModelAdmin):
    """
    Define the admin pages for documents.
    """
    ordering = ['id']
    list_display = ['title', 'created_at', 'status']
    list_filter = ['status']
    fieldsets = (
        (None, {'fields': ('id', 'title',)}),
        (
            _('Important dates'),
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            }
        ),
        (
            _('Document info'),
            {
                'fields': (
                    'repository_uri',
                    'repository_id',
                    'status',
                )
            }
        ),
    )
    readonly_fields = ['created_at', 'updated_at']

    def changelist_view(
            self, request: HttpRequest,
            extra_context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Customize the changelist view to include statistics in
        the admin template context.
        """
        extra_context = extra_context or {}
        extra_context['document_keywords_data'] = json.dumps(
            get_document_keywords_stats())
        return super().changelist_view(request, extra_context)

    def get_urls(self) -> list[URLPattern]:
        """
        Add custom admin URLs for exporting statistics to CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export-document-keywords-csv/', self.admin_site.admin_view(
                export_document_keywords_csv),
                name='document_keywords_stats_export'),
        ]
        return custom_urls + urls


class AuthoredDocumentAdmin(admin.ModelAdmin):
    """
    Define the admin pages for authored documents.
    """
    ordering = ['-created_at']
    list_display = ['author', 'document', 'created_at']
    list_filter = ['author']
    fieldsets = (
        (None, {
            'fields': ('author', 'document')
        }),
        ('Important dates', {
            'fields': ('created_at',)
        }),
    )
    readonly_fields = ['created_at']

    def changelist_view(
            self, request: HttpRequest,
            extra_context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Customize the changelist view to include statistics in
        the admin template context.
        """
        extra_context = extra_context or {}
        extra_context['author_stats_data'] = json.dumps(
            get_most_consulted_authors_stats())
        return super().changelist_view(request, extra_context)

    def get_urls(self) -> list[URLPattern]:
        """
        Add custom admin URLs for exporting statistics to CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export-authors-csv/', self.admin_site.admin_view(
                export_most_consulted_authors_csv),
                name='most_consulted_authors_stats_export'),
        ]
        return custom_urls + urls


class SavedDocumentAdmin(admin.ModelAdmin):
    """
    Define the admin pages for saved documents.
    """
    ordering = ['-created_at']
    list_display = ['user', 'document', 'created_at']
    list_filter = ['user']
    fieldsets = (
        (None, {
            'fields': ('user', 'document')
        }),
        ('Important dates', {
            'fields': ('created_at',)
        }),
    )
    readonly_fields = ['created_at']

    def changelist_view(
            self, request: HttpRequest,
            extra_context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Customize the changelist view to include statistics in
        the admin template context.
        """
        extra_context = extra_context or {}
        extra_context['document_stats_data'] = json.dumps(
            get_most_consulted_documents_stats())
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self) -> list[URLPattern]:
        """
        Add custom admin URLs for exporting statistics to CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export-documents-csv/', self.admin_site.admin_view(
                export_most_consulted_documents_csv),
                name='most_consulted_documents_stats_export'),
        ]
        return custom_urls + urls


class ChatSessionAdmin(admin.ModelAdmin):
    """
    Define the admin pages for chat sessions.
    """
    ordering = ['-created_at']
    list_display = ['user', 'session_name', 'created_at', 'updated_at']
    list_filter = ['user']
    fieldsets = (
        (None, {
            'fields': ('session_id', 'session_name', 'user', 'assistant_id')
        }),
        ('Important dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['session_name', 'assistant_id', 'user__email']

    def changelist_view(
            self, request: HttpRequest,
            extra_context: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """
        Customize the changelist view to include statistics in
        the admin template context.
        """
        extra_context = extra_context or {}
        extra_context['sessions_by_day'] = json.dumps(
            get_chats_over_time_stats())
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self) -> list[URLPattern]:
        """
        Add custom admin URLs for exporting statistics to CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export-chats-csv/', self.admin_site.admin_view(
                export_chats_over_time_csv),
                name='chats_over_time_stats_export'),
        ]
        return custom_urls + urls


admin.site.register(models.User, UserAdmin)
admin.site.register(models.FieldOfStudy)
admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.AuthoredDocument, AuthoredDocumentAdmin)
admin.site.register(models.SavedDocument, SavedDocumentAdmin)
admin.site.register(models.ChatSession, ChatSessionAdmin)
