#!/usr/bin/env python3
"""
Athens food recommender for Frankie.

Uses Matthew's local restaurant list as the source of truth. The goal is not to
rank the internet; it is to help Matthew pick from his own Athens list by mood,
cuisine, area, speed, rating, price, or pure spontaneous chaos.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "restaurants" / "athens_restaurants.csv"
REPORT_PATH = ROOT / "reports" / "ATHENS_FOOD_LAST.md"


MOOD_TAGS = {
    "adventurous": ["unique", "interesting", "fancy", "sit-down"],
    "bar": ["bar", "drinks", "pub", "brewery"],
    "beer": ["brewery", "drinks", "casual"],
    "breakfast": ["breakfast", "brunch", "bakery", "quick"],
    "brunch": ["breakfast", "brunch", "sit-down"],
    "budget": ["budget", "cheap"],
    "casual": ["casual", "quick", "neighborhood"],
    "cheap": ["budget", "cheap"],
    "chill": ["casual", "neighborhood", "cozy"],
    "classic": ["classic", "athens-classic", "local"],
    "coffee": ["cafe", "breakfast", "quick"],
    "comfort": ["comfort", "pub", "southern", "pizza", "bbq"],
    "cozy": ["cozy", "neighborhood", "classic"],
    "date": ["date-night", "fancy", "sit-down"],
    "date night": ["date-night", "fancy", "sit-down"],
    "dessert": ["dessert", "sweet"],
    "drinks": ["bar", "drinks", "brewery"],
    "fast": ["quick", "fast"],
    "fancy": ["fancy", "date-night"],
    "fresh": ["fresh", "healthy"],
    "healthy": ["healthy", "fresh", "bowls", "vegetarian"],
    "hot": ["hot-day", "fresh", "healthy", "quick"],
    "late": ["late-night", "bar", "pub"],
    "local": ["local", "athens-classic", "neighborhood"],
    "lunch": ["lunch", "quick", "fresh"],
    "mexican": ["mexican", "latin"],
    "outside": ["patio", "outdoor"],
    "patio": ["patio", "outdoor"],
    "quick": ["quick", "fast"],
    "random": [],
    "sit down": ["sit-down"],
    "spontaneous": [],
    "sweet": ["dessert", "sweet"],
    "takeout": ["quick", "to-go"],
    "vegetarian": ["vegetarian", "veggie"],
    "veggie": ["vegetarian", "veggie"],
    "vibes": ["vibes", "classic", "cozy"],
}


CLOSED_OR_INACTIVE_TERMS = [
    "i miss it",
    "miss it so much",
    "will it ever open back up",
    "catering only",
    "closing",
    "closed",
    "closed confirmed",
    "likely_closed",
    "inactive",
    "permanently closed",
    "menu is gone",
]

BAR_FOOD_CUISINES = {"bar", "pub", "brewery"}
FAST_FOOD_CUISINES = {"burgers", "fast food", "fast casual"}
FAST_FOOD_TEXT_TERMS = [
    "chain",
    "counter service",
    "counter-service",
    "fast casual",
    "fast-casual",
    "fast food",
    "quick service",
    "quick-service",
]
FAST_FOOD_SPEEDS = {"fast", "quicker"}
NEGATIVE_NOTE_TERMS = [
    "slow",
    "mid",
    "below mid",
    "too expensive",
    "not good",
    "bad",
    "weak",
]
HIDDEN_OUTPUT_TAGS = {
    "active-unverified",
    "directory-import",
    "has-address",
    "has-hours",
    "needs-verification",
    "osm",
    "source-openstreetmap",
    "source-visitathensga-com",
    "visit-athens",
}
DAY_INDEX = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


@dataclass
class Restaurant:
    name: str
    category: str
    rating: float | None
    cuisine: str
    speed: str
    price: float | None
    area: str
    got: str
    notes: str
    tags: list[str]

    @property
    def text(self) -> str:
        return " ".join(
            [
                self.name,
                self.category,
                self.cuisine,
                self.speed,
                self.area,
                self.got,
                self.notes,
                " ".join(self.tags),
            ]
        ).lower()


@dataclass
class Match:
    restaurant: Restaurant
    score: float
    reasons: list[str]


def parse_float(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def money(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value == int(value):
        return f"${int(value)}"
    return f"${value:.2f}"


def rating_text(value: float | None) -> str:
    if value is None:
        return "unrated"
    if value == int(value):
        return f"{int(value)}/5"
    return f"{value:g}/5"


def visible_tags(tags: list[str]) -> list[str]:
    return [tag for tag in tags if tag.lower() not in HIDDEN_OUTPUT_TAGS]


def load_restaurants() -> list[Restaurant]:
    if not DATA_CSV.exists():
        raise FileNotFoundError(f"Missing restaurant data: {DATA_CSV}")
    restaurants: list[Restaurant] = []
    with DATA_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            tags = [tag.strip() for tag in (row.get("tags") or "").split("|") if tag.strip()]
            restaurants.append(
                Restaurant(
                    name=(row.get("name") or "").strip(),
                    category=(row.get("category") or "").strip(),
                    rating=parse_float(row.get("star_rating") or ""),
                    cuisine=(row.get("cuisine") or "").strip(),
                    speed=(row.get("speed") or "").strip(),
                    price=parse_float(row.get("avg_price_per_meal") or ""),
                    area=(row.get("area") or "").strip(),
                    got=(row.get("what_i_got") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                    tags=tags,
                )
            )
    return [r for r in restaurants if r.name]


def expand_mood(mood: str) -> list[str]:
    mood = (mood or "").lower().strip()
    if not mood:
        return []
    tags: list[str] = []
    for phrase, mapped in MOOD_TAGS.items():
        if phrase in mood:
            tags.extend(mapped)
    tags.extend(token for token in re.split(r"[^a-z0-9]+", mood) if token)
    return unique(tags)


def unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        item = item.strip().lower()
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def contains(text: str, needle: str) -> bool:
    needle = needle.lower().strip()
    if not needle:
        return True
    if re.fullmatch(r"[a-z0-9]+", needle):
        return re.search(rf"\b{re.escape(needle)}s?\b", text.lower()) is not None
    return needle in text.lower()


def arg_terms(values: list[str] | None) -> list[str]:
    terms: list[str] = []
    for value in values or []:
        terms.extend(part.strip().lower() for part in value.split(","))
    return unique(terms)


def any_contains(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(contains(lowered, term) for term in terms)


def is_fast_food_like(restaurant: Restaurant) -> bool:
    cuisine_lower = restaurant.cuisine.lower()
    speed_lower = restaurant.speed.lower()
    tag_set = {tag.lower() for tag in restaurant.tags}
    if cuisine_lower in FAST_FOOD_CUISINES:
        return True
    if speed_lower in FAST_FOOD_SPEEDS:
        return True
    if tag_set.intersection(FAST_FOOD_SPEEDS):
        return True
    return any(term in restaurant.text for term in FAST_FOOD_TEXT_TERMS)


def is_bar_food_like(restaurant: Restaurant) -> bool:
    cuisine_lower = restaurant.cuisine.lower()
    tag_set = {tag.lower() for tag in restaurant.tags}
    if cuisine_lower in BAR_FOOD_CUISINES:
        return True
    return bool(tag_set.intersection(BAR_FOOD_CUISINES))


def likely_open_for_lunch_today(restaurant: Restaurant) -> bool:
    notes = restaurant.notes or ""
    match = re.search(r"OSM hours:\s*([^.;]+(?:; [^.;]+)*)", notes)
    if not match:
        return True
    hours = match.group(1).strip()
    if not hours or hours.lower() == "closed":
        return False
    today = DAY_INDEX[datetime.now().weekday()]
    applicable = []
    for segment in [part.strip() for part in hours.split(";") if part.strip()]:
        if segment_applies_today(segment, today):
            applicable.append(segment)
    if not applicable:
        return True
    found_time = False
    for segment in applicable:
        for start_h, start_m, end_h, end_m in re.findall(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", segment):
            found_time = True
            start = int(start_h) + int(start_m) / 60
            end = int(end_h) + int(end_m) / 60
            if start <= 13.0 and end >= 11.0:
                return True
    return not found_time


def segment_applies_today(segment: str, today: str) -> bool:
    days_part = segment.split()[0] if segment.split() else ""
    day_tokens = re.findall(r"\b(Mo|Tu|We|Th|Fr|Sa|Su)(?:-(Mo|Tu|We|Th|Fr|Sa|Su))?\b", days_part)
    if not day_tokens:
        return True
    for start, end in day_tokens:
        if not end and start == today:
            return True
        if end:
            start_i = DAY_INDEX.index(start)
            end_i = DAY_INDEX.index(end)
            today_i = DAY_INDEX.index(today)
            if start_i <= end_i and start_i <= today_i <= end_i:
                return True
            if start_i > end_i and (today_i >= start_i or today_i <= end_i):
                return True
    return False


def score_restaurant(restaurant: Restaurant, args: argparse.Namespace) -> Match | None:
    reasons: list[str] = []
    score = 0.0

    if not args.include_to_go and restaurant.category.lower() == "to go":
        return None
    if not args.include_closed and any(term in restaurant.text for term in CLOSED_OR_INACTIVE_TERMS):
        return None

    exclude_cuisines = arg_terms(args.exclude_cuisine)
    exclude_areas = arg_terms(args.exclude_area)
    exclude_speeds = arg_terms(args.exclude_speed)
    exclude_tags = arg_terms(args.exclude_tag)
    exclude_text = arg_terms(args.exclude)
    tag_set = set(restaurant.tags)
    cuisine_lower = restaurant.cuisine.lower()

    if args.cuisine and not contains(restaurant.cuisine, args.cuisine):
        return None
    if args.area and not contains(restaurant.area, args.area):
        return None
    if args.speed and not contains(restaurant.speed, args.speed):
        return None
    if args.no_bar_food and is_bar_food_like(restaurant):
        return None
    if args.no_fast_food and is_fast_food_like(restaurant):
        return None
    if exclude_cuisines and any_contains(restaurant.cuisine, exclude_cuisines):
        return None
    if exclude_areas and any_contains(restaurant.area, exclude_areas):
        return None
    if exclude_speeds and any_contains(restaurant.speed, exclude_speeds):
        return None
    if exclude_tags and any(term in tag_set for term in exclude_tags):
        return None
    if exclude_text and any_contains(restaurant.text, exclude_text):
        return None
    if args.max_price is not None:
        if restaurant.price is None or restaurant.price > args.max_price:
            return None
    if args.min_rating is not None:
        if restaurant.rating is None or restaurant.rating < args.min_rating:
            return None

    strict_query_terms = unique(re.split(r"[^a-z0-9]+", args.query.lower())) if args.query else []
    if strict_query_terms and not all(term in tag_set or contains(restaurant.text, term) for term in strict_query_terms):
        return None

    imported_row = "directory-import" in tag_set or "imported from" in restaurant.notes.lower()

    if restaurant.rating is not None:
        score += restaurant.rating * 18
        reasons.append(f"{rating_text(restaurant.rating)} rating")
    elif imported_row:
        score += 28
        reasons.append("directory import; needs Matthew try/rating")
    else:
        score += 45
        reasons.append("on the to-go/try list")

    if restaurant.price is not None:
        if restaurant.price <= 10:
            score += 8
            reasons.append(f"easy price at {money(restaurant.price)}")
        elif restaurant.price <= 15:
            score += 4
            reasons.append(f"reasonable price at {money(restaurant.price)}")

    query_terms = expand_mood(args.mood or "")
    if args.query:
        query_terms.extend(re.split(r"[^a-z0-9]+", args.query.lower()))
    query_terms = unique(query_terms)
    mood_text = " ".join([args.mood or "", args.query or ""]).lower()

    for term in query_terms:
        if term in tag_set:
            score += 14
            reasons.append(f"mood match: {term}")
        elif contains(restaurant.text, term):
            score += 6
            reasons.append(f"text match: {term}")

    if args.cuisine:
        score += 16
        reasons.append(f"cuisine match: {restaurant.cuisine}")
    if args.area:
        score += 8
        reasons.append(f"area match: {restaurant.area}")
    if args.speed:
        score += 8
        reasons.append(f"speed match: {restaurant.speed}")

    if restaurant.rating == 5:
        score += 5
    if "classic" in tag_set or "athens-classic" in tag_set:
        score += 3
    if "vibes" in tag_set:
        score += 3

    for term in NEGATIVE_NOTE_TERMS:
        if term in restaurant.notes.lower():
            score -= 8
            reasons.append(f"note caution: {term}")
            break

    if "date" in mood_text:
        if "date-night" in tag_set:
            score += 28
            reasons.append("proper date-night fit")
        elif "fancy" in tag_set:
            score += 18
            reasons.append("fancier option")
        elif "sit-down" in tag_set:
            score += 2
        else:
            score -= 20
        if cuisine_lower in {"breakfast", "brunch", "cafe"} and "brunch" not in mood_text:
            score -= 30
            reasons.append("brunch/breakfast, not dinner-date energy")

    if any(term in mood_text for term in ["lunch", "lunchtime"]):
        if not likely_open_for_lunch_today(restaurant):
            score -= 80
            reasons.append("saved hours look closed for lunch today")
        if "quick" in tag_set or restaurant.speed.lower() in {"fast", "quicker"}:
            score += 12
            reasons.append("good lunch speed")
        if "fresh" in tag_set or "healthy" in tag_set:
            score += 8
            reasons.append("lunch-friendly lighter option")
        if cuisine_lower in {"bar", "brewery"}:
            score -= 18
            reasons.append("less lunch-first")

    if any(term in mood_text for term in ["hot", "heat", "summer"]):
        if "fresh" in tag_set or "healthy" in tag_set or cuisine_lower in {"juice", "smoothies", "bowls", "poke"}:
            score += 16
            reasons.append("hot-weather friendly")
        if "comfort" in tag_set or cuisine_lower in {"bbq", "pub", "burgers", "mac and cheese"}:
            score -= 10
            reasons.append("heavier for a hot day")
        if "patio" in tag_set or "outdoor" in tag_set:
            score -= 8
            reasons.append("outdoor seating may be less ideal in heat")

    wants_drinks = any(term in mood_text for term in ["bar", "beer", "brewery", "drink", "cocktail"])
    if not wants_drinks and cuisine_lower == "brewery":
        score -= 20
        reasons.append("brewery, so better when drinks are the goal")
    if not wants_drinks and cuisine_lower == "bar" and any(
        term in restaurant.got.lower() for term in ["shots", "cocktail", "vodka", "neon cylinders"]
    ):
        score -= 14
        reasons.append("drink-forward, not food-first")

    if query_terms and not any(term in restaurant.text or term in tag_set for term in query_terms):
        score -= 15

    if score <= 0:
        return None
    return Match(restaurant=restaurant, score=score, reasons=unique(reasons))


def recommend(args: argparse.Namespace) -> list[Match]:
    matches = [score_restaurant(r, args) for r in load_restaurants()]
    cleaned = [match for match in matches if match is not None]
    cleaned.sort(key=lambda match: (match.score, match.restaurant.rating or 0, -(match.restaurant.price or 999)), reverse=True)
    if args.random:
        return randomize(cleaned, args.limit)
    return cleaned[: args.limit]


def randomize(matches: list[Match], limit: int) -> list[Match]:
    if not matches:
        return []
    pool = matches[: min(len(matches), 35)]
    rng = random.SystemRandom()
    first = rng.choices(pool, weights=[max(1, m.score) for m in pool], k=1)[0]
    rest = [m for m in pool if m.restaurant.name != first.restaurant.name]
    rng.shuffle(rest)
    return [first] + rest[: max(0, limit - 1)]


def list_values(kind: str) -> list[str]:
    restaurants = load_restaurants()
    if kind == "cuisines":
        return sorted({r.cuisine for r in restaurants if r.cuisine})
    if kind == "areas":
        return sorted({r.area for r in restaurants if r.area})
    if kind == "moods":
        return sorted(MOOD_TAGS)
    if kind == "tags":
        return sorted({tag for r in restaurants for tag in r.tags})
    raise ValueError(kind)


def render_report(matches: list[Match], args: argparse.Namespace) -> str:
    title = "Athens Food Pick"
    mode = "random/spontaneous" if args.random else "ranked recommendation"
    exclusions = []
    for label, values in [
        ("cuisine", arg_terms(args.exclude_cuisine)),
        ("area", arg_terms(args.exclude_area)),
        ("speed", arg_terms(args.exclude_speed)),
        ("tag", arg_terms(args.exclude_tag)),
        ("text", arg_terms(args.exclude)),
    ]:
        if values:
            exclusions.append(f"{label}: {', '.join(values)}")
    lines = [
        f"# {title}",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Mode:** {mode}",
        f"**Mood:** {args.mood or 'any'}",
        f"**Cuisine:** {args.cuisine or 'any'}",
        f"**Area:** {args.area or 'any'}",
        f"**Excluding:** {'; '.join(exclusions) if exclusions else 'nothing'}",
        "",
    ]
    if not matches:
        lines.extend(
            [
                "No matching restaurants found from the list.",
                "",
                "Try relaxing the area, cuisine, price, or rating filter.",
                "",
            ]
        )
        return "\n".join(lines)

    pick = matches[0].restaurant
    lines.extend(
        [
            f"## The Pick: {pick.name}",
            "",
            f"- **Rating:** {rating_text(pick.rating)}",
            f"- **Cuisine:** {pick.cuisine or 'unknown'}",
            f"- **Speed:** {pick.speed or 'unknown'}",
            f"- **Area:** {pick.area or 'unknown'}",
            f"- **Avg Price:** {money(pick.price)}",
            f"- **Tags:** {', '.join(visible_tags(pick.tags)) if visible_tags(pick.tags) else 'none'}",
            f"- **What Matthew got:** {pick.got or 'not listed'}",
            f"- **Notes:** {pick.notes or 'no notes'}",
            "",
            "### Why This One",
            "",
            ", ".join(matches[0].reasons[:6]) + ".",
            "",
        ]
    )

    backups = matches[1:]
    if backups:
        lines.extend(["## Backup Picks", ""])
        for index, match in enumerate(backups, 1):
            r = match.restaurant
            lines.extend(
                [
                    f"### {index}. {r.name}",
                    "",
                    f"- **Rating:** {rating_text(r.rating)}",
                    f"- **Cuisine / Area:** {r.cuisine or 'unknown'} / {r.area or 'unknown'}",
                    f"- **Price / Speed:** {money(r.price)} / {r.speed or 'unknown'}",
                    f"- **Why:** {', '.join(match.reasons[:4])}.",
                    f"- **Order idea:** {r.got or 'not listed'}",
                    "",
                ]
            )
    return "\n".join(lines)


def print_report(markdown: str) -> None:
    print(markdown)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(markdown, encoding="utf-8")
    print(f"\nReport written: {REPORT_PATH.relative_to(ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recommend an Athens restaurant from Matthew's list.")
    sub = parser.add_subparsers(dest="command")

    rec = sub.add_parser("recommend", help="Rank restaurants for a mood/cuisine/filter.")
    add_recommend_args(rec)
    rec.set_defaults(random=False)

    rnd = sub.add_parser("random", help="Make a spontaneous weighted random pick.")
    add_recommend_args(rnd)
    rnd.set_defaults(random=True)

    list_parser = sub.add_parser("list", help="List cuisines, areas, moods, or tags.")
    list_parser.add_argument("kind", choices=["cuisines", "areas", "moods", "tags"])

    args = parser.parse_args()
    if args.command is None:
        args.command = "recommend"
        args.mood = ""
        args.query = ""
        args.cuisine = ""
        args.area = ""
        args.speed = ""
        args.max_price = None
        args.min_rating = None
        args.exclude_cuisine = []
        args.exclude_area = []
        args.exclude_speed = []
        args.exclude_tag = []
        args.exclude = []
        args.limit = 5
        args.include_to_go = False
        args.include_closed = False
        args.no_bar_food = False
        args.no_fast_food = False
        args.random = False
    return args


def add_recommend_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mood", default="", help="Mood like cheap, date night, patio, vegetarian, breakfast.")
    parser.add_argument("--query", default="", help="Free-text search across notes, order, tags, and cuisine.")
    parser.add_argument("--cuisine", default="", help="Cuisine filter, such as mexican, italian, thai, dessert.")
    parser.add_argument("--area", default="", help="Area filter, such as dt, five points, normaltown, prince.")
    parser.add_argument("--speed", default="", help="Speed filter: fast, quicker, sit down.")
    parser.add_argument("--exclude-cuisine", action="append", default=[], help="Exclude cuisine(s), comma-separated or repeated.")
    parser.add_argument("--exclude-area", action="append", default=[], help="Exclude area(s), comma-separated or repeated.")
    parser.add_argument("--exclude-speed", action="append", default=[], help="Exclude speed(s), comma-separated or repeated.")
    parser.add_argument("--exclude-tag", action="append", default=[], help="Exclude derived tag(s), comma-separated or repeated.")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude text from name, cuisine, tags, notes, area, or order.")
    parser.add_argument("--no-bar-food", action="store_true", help="Exclude bar, pub, and brewery rows.")
    parser.add_argument("--no-fast-food", action="store_true", help="Exclude fast food, fast casual, chain, counter-service, and fast/quick-service rows.")
    parser.add_argument("--max-price", type=float, help="Maximum average price per meal.")
    parser.add_argument("--min-rating", type=float, help="Minimum star rating.")
    parser.add_argument("--limit", type=int, default=5, help="Number of picks to show.")
    parser.add_argument("--include-to-go", action="store_true", help="Include unrated to-go/try-list rows.")
    parser.add_argument("--include-closed", action="store_true", help="Include rows that the sheet notes as closed/inactive.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    if args.command == "list":
        for value in list_values(args.kind):
            print(value)
        return 0
    matches = recommend(args)
    print_report(render_report(matches, args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
