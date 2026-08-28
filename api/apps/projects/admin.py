from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "status", "start_date", "end_date", "created", "modified")
    list_filter = ("status",)
    search_fields = ("title", "slug", "organization__name", "organization__slug")
    readonly_fields = ("created", "modified")
