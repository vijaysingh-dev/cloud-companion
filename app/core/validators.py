from app.core.constants import CloudProviderEnum, Region


def normalize_provider(provider: str | CloudProviderEnum) -> CloudProviderEnum:
    """Normalize provider to CloudProviderEnum."""
    if isinstance(provider, CloudProviderEnum):
        return provider
    if isinstance(provider, str):
        provider_clean = provider.strip().lower()
        for candidate in CloudProviderEnum:
            if provider_clean in {candidate.value.lower(), candidate.name.lower()}:
                return candidate
    raise ValueError(
        f"Invalid cloud provider: {provider!r}. Expected one of {', '.join([p.value for p in CloudProviderEnum])}"
    )


def normalize_region(provider: CloudProviderEnum, region: str | list[str]) -> list[str]:
    """Normalize region(s) into list of valid region codes."""

    if not region:
        raise ValueError("Region must not be empty")

    if isinstance(region, str):
        regions = [r.strip().lower() for r in region.split(",") if r.strip()]
    elif isinstance(region, list):
        regions = [str(r).strip().lower() for r in region if str(r).strip()]
    else:
        raise ValueError("Region must be a string or list of strings")

    if not regions:
        raise ValueError("No valid regions provided")

    region_enum = {
        CloudProviderEnum.AWS: Region.AWS,
        CloudProviderEnum.AZURE: Region.AZURE,
        CloudProviderEnum.GCP: Region.GCP,
    }[provider]

    valid_regions = {r.code.lower() for r in region_enum}

    invalid = [r for r in regions if r not in valid_regions]
    if invalid:
        raise ValueError(
            f"Invalid region(s) for {provider.value}: {invalid}. "
            f"Valid regions: {sorted(valid_regions)}"
        )

    return regions
