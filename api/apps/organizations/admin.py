from django.contrib import admin

from .models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "organization_type", "parent", "slug", "created", "modified")
    list_filter = ("organization_type",)
    search_fields = ("name", "slug")
    readonly_fields = ("created", "modified")


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user_profile", "role", "created", "modified")
    list_filter = ("role",)
    search_fields = (
        "organization__name",
        "organization__slug",
        "user_profile__user__username",
        "user_profile__user__email",
    )
    readonly_fields = ("created", "modified")
