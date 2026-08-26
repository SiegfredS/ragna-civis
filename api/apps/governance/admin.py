from django.contrib import admin

from .models import GovernanceBody, GovernancePosition, GovernancePositionAssignment


@admin.register(GovernanceBody)
class GovernanceBodyAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "body_type", "created", "modified")
    list_filter = ("body_type",)
    search_fields = ("name", "organization__name", "organization__slug")
    readonly_fields = ("created", "modified")


@admin.register(GovernancePosition)
class GovernancePositionAdmin(admin.ModelAdmin):
    list_display = ("name", "governance_body", "created", "modified")
    search_fields = ("name", "governance_body__name", "governance_body__organization__name")
    readonly_fields = ("created", "modified")


@admin.register(GovernancePositionAssignment)
class GovernancePositionAssignmentAdmin(admin.ModelAdmin):
    list_display = ("position", "membership", "start_date", "end_date", "created", "modified")
    list_filter = ("start_date", "end_date")
    search_fields = (
        "position__name",
        "membership__organization__name",
        "membership__user_profile__user__username",
        "membership__user_profile__user__email",
    )
    readonly_fields = ("created", "modified")
