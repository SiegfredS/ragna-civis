from django.contrib import admin

from apps.organizations.models import OrganizationMembership
from apps.profiles.admin import OrganizationMembershipInline, UserProfileAdmin
from apps.profiles.models import UserProfile


class TestUserProfileAdmin:
    def test_includes_organization_membership_editor(self):
        model_admin = UserProfileAdmin(UserProfile, admin.site)

        assert model_admin.inlines == (OrganizationMembershipInline,)
        assert OrganizationMembershipInline.model is OrganizationMembership
        assert OrganizationMembershipInline.fk_name == "user_profile"
        assert OrganizationMembershipInline.fields == ("organization", "role")
        assert OrganizationMembershipInline.show_change_link is True
