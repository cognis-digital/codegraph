"""Transformation stage: cleaning and enrichment."""


def clean_rows(rows):
    """Normalize whitespace and casing."""
    return [normalize_row(r) for r in rows]


def normalize_row(row):
    """Strip and title-case the name field."""
    out = dict(row)
    out["name"] = row["name"].strip().title()
    return out


def enrich_rows(rows):
    """Add a derived region from the country code."""
    return [dict(r, region=region_for(r["country"])) for r in rows]


def region_for(country):
    """Map an ISO country code to a coarse region."""
    return {"us": "NA", "ca": "NA", "de": "EU"}.get(country, "OTHER")
