import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path


def _safe_get_list(value) -> Optional[List[str]]:
    """Normalize CSV field to a Python list if possible.

    Accepts a JSON array string, a comma-separated string, or already a list.
    Returns None if empty.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        # Try JSON-like list
        if v.startswith("[") and v.endswith("]"):
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
        # Comma separated
        parts = [p.strip() for p in v.split(",") if p.strip()]
        return parts if parts else None
    return None


def load_bakery_csv(csv_path: str) -> List[Dict]:
    """Load bakery data from CSV.

    This loader does NOT perform any tag extraction. It expects the CSV to
    include a `bread_tags` column (optional) that already contains the
    tags for each bakery (as a JSON array string or comma-separated string).
    """
    df = pd.read_csv(csv_path)

    # Clean up the dataframe
    df = df.fillna("")

    bakeries = []
    for _, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        ai_summary = str(row.get("aisummary", "")).strip() if row.get("aisummary") else ""

        bread_tags_raw = row.get("bread_tags") if "bread_tags" in row else None
        bread_tags = _safe_get_list(bread_tags_raw)

        bakery = {
            "name": name,
            "shop_id": str(row.get("id", "")).strip() if row.get("id") else None,
            "rating": float(row.get("rating")) if row.get("rating") and str(row.get("rating")) != "" else None,
            "address": str(row.get("address", "")).strip(),
            "category": None,
            "district": None,
            "opening_hours": None,
            "ai_summary": ai_summary,
            "bread_tags": bread_tags,
        }
        bakeries.append(bakery)

    return bakeries


def load_bakery_csv_with_reviews(csv_path: str, reviews: Dict[str, List[str]]) -> List[Dict]:
    """Load bakeries and attach provided reviews.

    This function will NOT attempt to extract tags from reviews. If `bread_tags`
    are already present in the CSV they will be preserved; otherwise they remain
    empty/None and the provided reviews are attached under a `reviews` key.
    """
    bakeries = load_bakery_csv(csv_path)

    for bakery in bakeries:
        shop_id = bakery.get("shop_id")
        if shop_id and shop_id in reviews:
            bakery["reviews"] = reviews[shop_id]
    return bakeries


def extract_district(address: str) -> str:
    """Extract district from address"""
    districts = ["권선구", "영통구", "팔달구", "장안구"]
    for district in districts:
        if district in address:
            return district
    return None


def validate_bakery_data(bakery: Dict) -> bool:
    """Validate bakery data"""
    if not bakery.get("name"):
        return False
    if not bakery.get("address"):
        return False
    return True
