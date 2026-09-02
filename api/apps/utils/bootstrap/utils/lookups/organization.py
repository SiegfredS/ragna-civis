from apps.organizations.models import Organization


def get_organization(*, slug: str) -> Organization:
    try:
        return Organization.objects.get(slug=slug)
    except Organization.DoesNotExist as error:
        raise ValueError(f"Bootstrap organization with slug {slug!r} does not exist.") from error
    except Organization.MultipleObjectsReturned as error:
        raise ValueError(f"Bootstrap organization with slug {slug!r} is ambiguous.") from error
