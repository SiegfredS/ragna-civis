from django.contrib import admin

from apps.governance.models import GovernanceBody, GovernancePositionAssignment
from apps.projects.models import Project

from .models import Organization, OrganizationMembership


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    fk_name = "organization"
    extra = 0
    autocomplete_fields = ("user_profile",)
    show_change_link = True
    fields = ("user_profile", "role")


class GovernancePositionAssignmentInline(admin.TabularInline):
    model = GovernancePositionAssignment
    fk_name = "membership"
    extra = 0
    autocomplete_fields = ("position",)
    show_change_link = True
    fields = ("position", "start_date", "end_date")


class ChildOrganizationInline(admin.TabularInline):
    model = Organization
    fk_name = "parent"
    extra = 0
    show_change_link = True
    fields = ("name", "slug", "organization_type")


class GovernanceBodyInline(admin.TabularInline):
    model = GovernanceBody
    fk_name = "organization"
    extra = 0
    show_change_link = True
    fields = ("name", "body_type")


class ProjectInline(admin.TabularInline):
    model = Project
    fk_name = "organization"
    extra = 0
    show_change_link = True
    fields = ("title", "slug", "status", "start_date", "end_date")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "organization_type", "parent", "slug", "created", "modified")
    list_filter = ("organization_type",)
    search_fields = ("name", "slug")
    readonly_fields = ("created", "modified")
    inlines = (OrganizationMembershipInline, ChildOrganizationInline, GovernanceBodyInline, ProjectInline)


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
    inlines = (GovernancePositionAssignmentInline,)
