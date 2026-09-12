from django.contrib import admin

from apps.organizations.models import OrganizationMembership

from .models import UserProfile


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    fk_name = "user_profile"
    extra = 0
    autocomplete_fields = ("organization",)
    show_change_link = True
    fields = ("organization", "role")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created", "modified")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("created", "modified")
    inlines = (OrganizationMembershipInline,)
