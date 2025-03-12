"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


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


class DocumentAdmin(admin.ModelAdmin):
    """
    Define the admin pages for documents.
    """
    ordering = ['id']
    list_display = ['title', 'created_at']
    fieldsets = (
        (None, {'fields': ('title',)}),
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
                    'status',
                )
            }
        ),
    )
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.FieldOfStudy)
admin.site.register(models.Document, DocumentAdmin)
