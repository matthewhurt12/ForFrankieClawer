#!/usr/bin/env python3
"""
Refresh the Athens restaurant CSV from public directory sources.

The spreadsheet-derived rows stay intact. Imported rows are marked as lower
confidence so they expand discovery without pretending Matthew has tried them.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin

import requests


ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "restaurants" / "athens_restaurants.csv"
ENRICHMENT_DIR = ROOT / "data" / "restaurants" / "enrichment"
REPORT_PATH = ROOT / "reports" / "ATHENS_RESTAURANT_REFRESH_001.md"

FIELDNAMES = [
    "category",
    "name",
    "star_rating",
    "cuisine",
    "speed",
    "avg_price_per_meal",
    "area",
    "what_i_got",
    "notes",
    "tags",
]

VISIT_ATHENS_PAGES = [
    "https://www.visitathensga.com/restaurants/",
    "https://www.visitathensga.com/restaurants/award-winning-dining/",
    "https://www.visitathensga.com/restaurants/black-owned-restaurants/",
    "https://www.visitathensga.com/restaurants/craft-breweries/",
]

OVERPASS_QUERY = r"""
[out:json][timeout:60];
(
  node["amenity"~"restaurant|cafe|fast_food|bar|pub|ice_cream|food_court|biergarten"](33.86,-83.52,34.08,-83.24);
  way["amenity"~"restaurant|cafe|fast_food|bar|pub|ice_cream|food_court|biergarten"](33.86,-83.52,34.08,-83.24);
  relation["amenity"~"restaurant|cafe|fast_food|bar|pub|ice_cream|food_court|biergarten"](33.86,-83.52,34.08,-83.24);
  node["shop"~"bakery|coffee|confectionery"](33.86,-83.52,34.08,-83.24);
  way["shop"~"bakery|coffee|confectionery"](33.86,-83.52,34.08,-83.24);
);
out center tags;
"""

CLOSURE_OVERRIDES = {
    "birdies": "LIKELY_CLOSED: Google/Yelp/Red & Black snippets indicated Birdies Market closed/was closing in late 2025; verify before use.",
    "grit": "CLOSED: Sheet already says Matthew misses it; The Grit closed in 2022.",
    "the grit": "CLOSED: Sheet already says Matthew misses it; The Grit closed in 2022.",
    "home made": "CLOSED: Flagpole/Banner-Herald reported home.made permanently closed on Baxter Street in 2024.",
    "weaver d's": "CLOSED: WUGA/AJC reported Weaver D's closed in February 2026.",
    "weaver ds": "CLOSED: WUGA/AJC reported Weaver D's closed in February 2026.",
    "weaver d's delicious fine foods": "CLOSED: WUGA/AJC reported Weaver D's closed in February 2026.",
    "weaver ds delicious fine foods": "CLOSED: WUGA/AJC reported Weaver D's closed in February 2026.",
}

CHAIN_HINTS = {
    "applebee",
    "arby's",
    "barberitos",
    "baskin",
    "bojangles",
    "burger king",
    "captain d",
    "carrabba",
    "cava",
    "checkers",
    "cheddar",
    "chick-fil-a",
    "chili",
    "chipotle",
    "cici",
    "cook out",
    "cracker barrel",
    "dairy queen",
    "domino",
    "dunkin",
    "einstein",
    "firehouse",
    "five guys",
    "freddy",
    "hardee",
    "ihop",
    "jersey mike",
    "jimmy john",
    "kfc",
    "krystal",
    "little caesars",
    "longhorn",
    "mcalister",
    "mcdonald",
    "newk",
    "olive garden",
    "outback",
    "panda express",
    "panera",
    "papa john",
    "pizza hut",
    "popeyes",
    "raising cane",
    "red lobster",
    "schlotzsky",
    "smoothie king",
    "sonic",
    "starbucks",
    "subway",
    "taco bell",
    "texas roadhouse",
    "waffle house",
    "wendy",
    "zaxby",
}


@dataclass
class Candidate:
    name: str
    cuisine: str = ""
    speed: str = ""
    area: str = ""
    address: str = ""
    source: str = ""
    source_url: str = ""
    website: str = ""
    opening_hours: str = ""
    lat: float | None = None
    lon: float | None = None
    tags: list[str] | None = None


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href") or ""
        if "/listing/" in href:
            self.links.add(href)


def normalize_name(value: str) -> str:
    value = unquote(value or "").lower()
    value = re.sub(r"['’]s\b", "s", value)
    value = value.replace("&", "and")
    value = re.sub(r"\b(co\.|company|restaurant|cafe|grill|kitchen|bar|pub)\b", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_name_key(value: str) -> str:
    compact = normalize_name(value).replace(" ", "")
    if compact.endswith("bar") and len(compact) > 6:
        compact = compact[:-3]
    return compact


def display_name(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value


def unique_tags(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for tag in tags:
        clean = re.sub(r"[^a-z0-9+-]+", "-", tag.lower()).strip("-")
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def load_rows() -> list[dict[str, str]]:
    with DATA_CSV.open("r", encoding="utf-8", newline="") as f:
        return [{field: row.get(field, "") for field in FIELDNAMES} for row in csv.DictReader(f)]


def write_rows(rows: list[dict[str, str]]) -> None:
    with DATA_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def fetch_visit_athens() -> list[Candidate]:
    candidates: dict[str, Candidate] = {}
    session = requests.Session()
    session.headers.update({"User-Agent": "FrankieMindRestaurantRefresh/1.0"})
    for page in VISIT_ATHENS_PAGES:
        try:
            html = session.get(page, timeout=30).text
        except requests.RequestException:
            continue
        parser = LinkParser()
        parser.feed(html)
        for href in parser.links:
            url = urljoin(page, href)
            slug = url.rstrip("/").split("/")[-2]
            if slug.isdigit():
                slug = url.rstrip("/").split("/")[-3]
            name = title_from_slug(slug)
            key = normalize_name(name)
            if not key:
                continue
            tags = ["visit-athens", "directory-import", "active-unverified"]
            if "craft-breweries" in page:
                tags.extend(["brewery", "drinks"])
            if "black-owned" in page:
                tags.append("black-owned")
            if "award-winning" in page:
                tags.append("award-winning")
            candidates[key] = Candidate(
                name=name,
                cuisine=infer_cuisine(name, "", tags),
                speed=infer_speed("", "", tags),
                area=infer_area(name=name, address="", lat=None, lon=None),
                source="visitathensga.com",
                source_url=url,
                tags=tags,
            )
    return list(candidates.values())


def title_from_slug(slug: str) -> str:
    replacements = {
        "five-%26-ten": "Five & Ten",
        "clocked!": "Clocked!",
        "puma-yus": "Puma Yu's",
        "mamas-boy": "Mama's Boy",
        "dawg-gone-good-bbq": "Dawg Gone Good BBQ",
        "teds-most-best": "Ted's Most Best",
    }
    if slug in replacements:
        return replacements[slug]
    text = unquote(slug).replace("%26", "&").replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text.title().replace(" Bbq", " BBQ").replace(" Ga ", " GA ")


def fetch_osm() -> list[Candidate]:
    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": OVERPASS_QUERY},
        timeout=120,
        headers={"User-Agent": "FrankieMindRestaurantRefresh/1.0"},
    )
    response.raise_for_status()
    data = response.json()
    ENRICHMENT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    (ENRICHMENT_DIR / f"osm_restaurants_{stamp}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    candidates: dict[str, Candidate] = {}
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = display_name(tags.get("name", ""))
        if not name:
            continue
        if tags.get("disused:amenity") or tags.get("abandoned:amenity"):
            continue
        if (tags.get("opening_hours") or "").strip().lower() == "closed":
            source_tags = ["osm", "directory-import", "closed", "inactive", "needs-verification"]
        else:
            source_tags = ["osm", "directory-import", "active-unverified"]
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")
        address = format_address(tags)
        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        cuisine = infer_cuisine(name, tags.get("cuisine", "") or amenity or shop, [])
        speed = infer_speed(amenity, shop, [])
        area = infer_area(name=name, address=address, lat=lat, lon=lon)
        if amenity:
            source_tags.append(amenity)
        if shop:
            source_tags.append(shop)
        if cuisine:
            source_tags.append(cuisine)
        if tags.get("brand") or is_chain(name):
            source_tags.append("chain")
        if amenity == "fast_food":
            source_tags.extend(["fast-food", "fast-casual"])
        if tags.get("opening_hours"):
            source_tags.append("has-hours")
        key = normalize_name(name)
        existing = candidates.get(key)
        candidate = Candidate(
            name=name,
            cuisine=cuisine,
            speed=speed,
            area=area,
            address=address,
            source="openstreetmap",
            source_url=f"https://www.openstreetmap.org/{element.get('type')}/{element.get('id')}",
            website=tags.get("website", ""),
            opening_hours=tags.get("opening_hours", ""),
            lat=float(lat) if lat is not None else None,
            lon=float(lon) if lon is not None else None,
            tags=source_tags,
        )
        if not existing or candidate.address:
            candidates[key] = candidate
    return list(candidates.values())


def format_address(tags: dict[str, str]) -> str:
    parts = []
    street = " ".join(part for part in [tags.get("addr:housenumber", ""), tags.get("addr:street", "")] if part).strip()
    if street:
        parts.append(street)
    if tags.get("addr:city"):
        parts.append(tags["addr:city"])
    if tags.get("addr:postcode"):
        parts.append(tags["addr:postcode"])
    return ", ".join(parts)


def infer_cuisine(name: str, raw: str, tags: list[str]) -> str:
    text = " ".join([name, raw, " ".join(tags)]).lower()
    raw = (raw or "").replace(";", " / ").replace("_", " ").strip().lower()
    mapping = [
        ("coffee", "coffee"),
        ("bagel", "breakfast"),
        ("bakery", "bakery"),
        ("barbecue", "bbq"),
        ("bbq", "bbq"),
        ("korean", "korean"),
        ("burger", "burgers"),
        ("pizza", "pizza"),
        ("ramen", "japanese"),
        ("sushi", "sushi"),
        ("hibachi", "japanese"),
        ("thai", "thai"),
        ("pho", "vietnamese"),
        ("vietnam", "vietnamese"),
        ("ethiopian", "ethiopian"),
        ("jamaican", "jamaican"),
        ("indian", "indian"),
        ("mexican", "mexican"),
        ("taco", "mexican"),
        ("mediterranean", "mediterranean"),
        ("italian", "italian"),
        ("seafood", "seafood"),
        ("oyster", "seafood"),
        ("ice cream", "dessert"),
        ("chocolate", "dessert"),
        ("cookie", "dessert"),
        ("brewery", "brewery"),
        ("pub", "pub"),
        ("bar", "bar"),
        ("sandwich", "sandwich"),
        ("deli", "deli"),
        ("soul", "soul"),
        ("southern", "southern"),
        ("vegan", "vegan"),
        ("vegetarian", "vegetarian"),
    ]
    for needle, cuisine in mapping:
        if needle in text:
            return cuisine
    return raw.split(" / ")[0] if raw else "restaurant"


def infer_speed(amenity: str, shop: str, tags: list[str]) -> str:
    text = " ".join([amenity, shop, " ".join(tags)]).lower()
    if "fast_food" in text or "ice_cream" in text:
        return "fast"
    if any(term in text for term in ["cafe", "bakery", "coffee", "confectionery"]):
        return "quicker"
    if any(term in text for term in ["bar", "pub", "brewery", "biergarten"]):
        return "fast"
    return "sit down"


def infer_area(name: str, address: str, lat: float | None, lon: float | None) -> str:
    text = f"{name} {address}".lower()
    if any(term in text for term in ["lumpkin", "five points", "milledge", "south lumpkin"]):
        return "five points"
    if any(term in text for term in ["prince", "normaltown", "hiawassee", "chase"]):
        return "normaltown/prince"
    if any(term in text for term in ["alps", "atlanta hwy", "epps bridge", "oconee connector"]):
        return "west athens"
    if any(term in text for term in ["barnett shoals", "gaines school", "lexington", "college station"]):
        return "eastside"
    if "watkinsville" in text:
        return "watkinsville"
    if "winterville" in text:
        return "winterville"
    if "bogart" in text:
        return "bogart"
    if lat is not None and lon is not None:
        if lon > -83.39 and lat > 33.94:
            return "dt"
        if lon > -83.37:
            return "eastside"
        if lon < -83.42:
            return "west athens"
    return "athens area"


def is_chain(name: str) -> bool:
    lowered = name.lower()
    return any(hint in lowered for hint in CHAIN_HINTS)


def merge_candidates(rows: list[dict[str, str]], candidates: list[Candidate]) -> tuple[list[dict[str, str]], list[Candidate], list[str]]:
    by_name = {canonical_name_key(row["name"]): row for row in rows if row.get("name")}
    added: list[Candidate] = []
    touched: list[str] = []

    for row in rows:
        key = normalize_name(row.get("name", ""))
        closure = CLOSURE_OVERRIDES.get(key)
        if closure and "closed" not in row.get("tags", "").lower():
            row["notes"] = append_note(row.get("notes", ""), closure)
            row["tags"] = merge_tag_string(row.get("tags", ""), ["closed", "inactive", "needs-verification"])
            touched.append(row.get("name", ""))

    for candidate in candidates:
        key = canonical_name_key(candidate.name)
        if not key or key in by_name:
            existing = by_name.get(key)
            if existing:
                tags = [f"source-{candidate.source}"] + (candidate.tags or [])
                if candidate.source == "visitathensga.com":
                    tags.append("visit-athens")
                existing["tags"] = merge_tag_string(existing.get("tags", ""), tags)
                if "closed" in (candidate.tags or []):
                    existing["notes"] = append_note(existing.get("notes", ""), "OSM opening_hours is closed; verify before use.")
                if candidate.opening_hours and "hours:" not in existing.get("notes", "").lower():
                    existing["notes"] = append_note(existing.get("notes", ""), f"OSM hours: {candidate.opening_hours}")
            continue

        tags = unique_tags(candidate.tags or [])
        if is_chain(candidate.name):
            tags.append("chain")
        if "closed" in (candidate.tags or []):
            continue
        if candidate.address:
            tags.append("has-address")
        note_bits = [
            f"Imported from {candidate.source}; needs Matthew try/rating.",
        ]
        if candidate.address:
            note_bits.append(f"Address: {candidate.address}.")
        if candidate.opening_hours:
            note_bits.append(f"OSM hours: {candidate.opening_hours}.")
        row = {
            "category": "Directory Import",
            "name": candidate.name.lower(),
            "star_rating": "",
            "cuisine": candidate.cuisine,
            "speed": candidate.speed,
            "avg_price_per_meal": "",
            "area": candidate.area,
            "what_i_got": "",
            "notes": " ".join(note_bits),
            "tags": "|".join(unique_tags(tags)),
        }
        rows.append(row)
        by_name[key] = row
        added.append(candidate)
    rows, duplicate_count = dedupe_rows(rows)
    if duplicate_count:
        touched.append(f"deduped {duplicate_count} duplicate directory/name rows")
    return rows, added, touched


def dedupe_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    by_key: dict[str, dict[str, str]] = {}
    removed = 0
    for row in rows:
        key = canonical_name_key(row.get("name", ""))
        if not key:
            continue
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = row
            continue

        keep, drop = choose_row(existing, row)
        merge_row(keep, drop)
        by_key[key] = keep
        removed += 1
    return list(by_key.values()), removed


def choose_row(left: dict[str, str], right: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    def priority(row: dict[str, str]) -> tuple[int, int, int]:
        category = row.get("category", "")
        category_score = 3 if category == "Full Restaurant List" else 2 if category == "To Go" else 1
        rating_score = 1 if row.get("star_rating") else 0
        note_score = len(row.get("notes", ""))
        return (category_score, rating_score, note_score)

    return (left, right) if priority(left) >= priority(right) else (right, left)


def merge_row(keep: dict[str, str], drop: dict[str, str]) -> None:
    keep["tags"] = merge_tag_string(keep.get("tags", ""), [tag for tag in drop.get("tags", "").split("|") if tag])
    for field in ["cuisine", "speed", "area", "what_i_got", "star_rating", "avg_price_per_meal"]:
        if not keep.get(field) and drop.get(field):
            keep[field] = drop[field]
    drop_note = drop.get("notes", "")
    if drop_note and "Imported from" in drop_note and "source-openstreetmap" not in keep.get("tags", ""):
        keep["notes"] = append_note(keep.get("notes", ""), "Directory source also found this place; details may need verification.")


def append_note(existing: str, note: str) -> str:
    existing = (existing or "").strip()
    if not existing:
        return note
    if note.lower() in existing.lower():
        return existing
    return f"{existing}; {note}"


def merge_tag_string(existing: str, new_tags: list[str]) -> str:
    tags = [tag.strip() for tag in (existing or "").split("|") if tag.strip()]
    tags.extend(new_tags)
    return "|".join(unique_tags(tags))


def write_report(before_count: int, rows: list[dict[str, str]], added: list[Candidate], touched: list[str], source_counts: dict[str, int]) -> None:
    category_imports = [row for row in rows if row.get("category") == "Directory Import"]
    source_rows = [row for row in rows if "directory-import" in row.get("tags", "")]
    chains = [row for row in source_rows if "chain" in row.get("tags", "")]
    lines = [
        "# Athens Restaurant Refresh",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Summary",
        "",
        f"- Started with {before_count} rows.",
        f"- Ended with {len(rows)} rows.",
        f"- Added {len(added)} new directory-import rows.",
        f"- Marked/updated {len(touched)} likely closed or needs-verification rows.",
        f"- Directory Import category rows currently in CSV: {len(category_imports)}.",
        f"- Rows carrying public directory source tags: {len(source_rows)}.",
        f"- Public-directory rows tagged as chains: {len(chains)}.",
        "",
        "## Sources Used",
        "",
        f"- OpenStreetMap / Overpass: {source_counts.get('openstreetmap', 0)} candidate records fetched from the Athens-area bounding box.",
        f"- Visit Athens restaurant pages: {source_counts.get('visitathensga.com', 0)} curated listing links fetched.",
        "",
        "## Closed / Inactive Updates",
        "",
    ]
    if touched:
        for name in sorted(set(touched)):
            lines.append(f"- {name}")
    else:
        lines.append("- None")
    lines.extend(["", "## New Rows Added", ""])
    for candidate in sorted(added, key=lambda c: c.name.lower())[:125]:
        bits = [candidate.source]
        if candidate.cuisine:
            bits.append(candidate.cuisine)
        if candidate.area:
            bits.append(candidate.area)
        if candidate.address:
            bits.append(candidate.address)
        lines.append(f"- {candidate.name} ({'; '.join(bits)})")
    if len(added) > 125:
        lines.append(f"- ...and {len(added) - 125} more.")
    lines.extend(
        [
            "",
            "## Notes For Frankie",
            "",
            "- Imported rows are discovery candidates, not Matthew-rated favorites.",
            "- Keep using Google/Apify verification for current hours before a go-now pick.",
            "- Rows tagged `chain`, `fast-food`, or `fast-casual` should be rejected when Matthew says no fast food.",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = load_rows()
    before_count = len(rows)
    osm = fetch_osm()
    visit = fetch_visit_athens()
    candidates = osm + visit
    rows, added, touched = merge_candidates(rows, candidates)
    rows.sort(key=lambda row: (row.get("category", ""), normalize_name(row.get("name", ""))))
    write_rows(rows)
    write_report(
        before_count=before_count,
        rows=rows,
        added=added,
        touched=touched,
        source_counts={"openstreetmap": len(osm), "visitathensga.com": len(visit)},
    )
    print(f"Started with {before_count} rows")
    print(f"Ended with {len(rows)} rows")
    print(f"Added {len(added)} rows")
    print(f"Updated closed/inactive: {len(touched)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
