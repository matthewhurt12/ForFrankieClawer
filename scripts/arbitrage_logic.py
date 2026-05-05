#!/usr/bin/env python3
"""
Shared conservative lead logic for the vintage audio arbitrage system.

This module is intentionally boring and explicit. Frankie/OpenClaw can import it
from multiple scripts without having to remember which older report was safe.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import Any


MERCARI_CSV = Path("data/external_leads/mercari_leads.csv")
FACEBOOK_CSV = Path("data/external_leads/facebook_marketplace_leads.csv")
CLEAN_SOLD_COMPS_CSV = Path("data/ebay_sold_comps_clean.csv")


HARD_REJECT_TERMS = [
    "manual",
    "brochure",
    "catalog",
    "service manual",
    "pdf",
    "led",
    "lamp",
    "lamps",
    "bulb",
    "bulbs",
    "kit",
    "parts",
    "part only",
    "parts only",
    "for parts",
    "capacitor",
    "knob",
    "faceplate",
    "decal",
    "sticker",
    "switch",
    "button",
    "cable",
    "repair",
    "rebuild",
    "cabinet only",
    "case only",
    "wood case only",
    "wood cabinet only",
    "mainboard",
    "motherboard",
    "plinth",
    "upgrade",
    "cartridge",
    "headshell",
    "stylus",
    "needle",
    "dust cover",
    "dustcover",
    "mat",
    "tonearm",
    "platter",
    "remote only",
    "feet",
    "cord only",
    "poster",
    "shirt",
    "t-shirt",
    "tee",
    "hoodie",
    "hat",
    "pin",
    "enamel",
    "badge",
    "logo",
    "hinge",
    "mount",
    "holder",
    "antenna",
    "relay",
    "fuse",
    "board",
    "volume function",
    "volume control",
    "function button",
    "bias button",
    "level button",
    "disc only",
    "game only",
    "case only",
    "box only",
    "empty box",
    "manual only",
    "controller only",
    "controllers only",
    "remote only",
    "charger only",
    "power supply only",
    "adapter only",
    "replacement shell",
    "screen protector",
    "glass",
    "dial",
    "meter",
    "cash for",
    "we buy",
    "buying",
    "wanted",
]


EQUIPMENT_TERMS = [
    "receiver",
    "stereo receiver",
    "am/fm receiver",
    "amplifier",
    "integrated amplifier",
    "power amp",
    "preamp",
    "preamplifier",
    "turntable",
    "record player",
    "direct drive",
    "cassette deck",
    "tape deck",
    "reel to reel",
    "reel-to-reel",
    "speaker",
    "speakers",
    "tuner",
    "equalizer",
    "cd player",
    "console",
    "game console",
    "nintendo",
    "gamecube",
    "playstation",
    "xbox",
    "sega",
    "macintosh",
    "imac",
    "power mac",
    "ipod",
    "walkman",
    "discman",
    "minidisc",
    "computer",
    "deck",
    "stereo",
]


POSITIVE_CONDITION_TERMS = [
    "working",
    "tested",
    "serviced",
    "restored",
    "excellent",
    "powers on",
    "fully functional",
]


NEGATIVE_CONDITION_TERMS = [
    "as-is",
    "as is",
    "untested",
    "not working",
    "broken",
    "needs work",
    "needs repair",
    "needs tlc",
    "no sound",
    "hum",
    "dead channel",
]


MODERN_AV_TERMS = [
    "home theater",
    "multi channel",
    "multichannel",
    "surround",
    "hdmi",
    "4k",
    "av receiver",
    "a/v receiver",
    "blu-ray",
    "blu ray",
    "dolby digital",
    "str-dh",
    "str-de",
    "str-se",
]


BRANDS = [
    "mcintosh",
    "pioneer",
    "marantz",
    "sansui",
    "technics",
    "nakamichi",
    "jbl",
    "yamaha",
    "sony",
    "harman kardon",
    "harmon kardon",
    "harmon kardan",
    "nintendo",
    "sega",
    "microsoft",
    "xbox",
    "apple",
    "atari",
    "kenwood",
    "denon",
    "teac",
    "tascam",
    "revox",
    "akai",
    "rotel",
]


MODEL_PRICE_FLOORS = {
    "McIntosh MA 5100": 500,
    "McIntosh MA 6100": 500,
    "McIntosh C22": 500,
    "McIntosh MC 2300": 500,
    "Pioneer SX-1250": 400,
    "Pioneer SX-1050": 400,
    "Pioneer SX-950": 400,
    "Pioneer SX-850": 400,
    "Pioneer SX-770": 400,
    "Pioneer SX-650": 400,
    "Marantz 2270": 400,
    "Marantz 2275": 400,
    "Marantz 2245": 400,
    "Marantz 2226B": 250,
    "Technics SA-5370": 150,
    "Sansui G-9000": 400,
    "Sansui 9090": 400,
    "Technics SL-1200": 300,
    "Technics SL-1210": 300,
    "Technics SL-D35": 50,
    "Nakamichi Dragon": 700,
    "Nakamichi 1000ZXL": 700,
    "Nakamichi CR-7A": 75,
    "Nakamichi ZX-7": 75,
    "Nakamichi ZX-9": 75,
    "Nakamichi BX-300": 75,
    "JBL L100": 300,
    "Realistic STA-82": 50,
    "Pioneer PL-600": 75,
    "U-Turn Orbit": 75,
    "Nintendo Wii": 25,
    "Nintendo Wii U": 70,
    "Nintendo GameCube": 50,
    "Nintendo 64": 50,
    "Super Nintendo": 50,
    "Nintendo NES": 50,
    "Sony PlayStation 2": 35,
    "Sony PlayStation 3": 40,
    "Sega Dreamcast": 100,
    "Sega Genesis": 30,
    "Xbox 360": 30,
    "Original Xbox": 40,
    "Apple iMac G3": 100,
    "Apple iMac G4": 150,
    "Apple iMac G5": 75,
    "Apple Power Mac G4": 100,
    "Power Mac G4 Cube": 300,
    "Macintosh Plus": 150,
    "Macintosh Classic": 150,
    "Macintosh SE": 150,
    "Apple II": 150,
    "iPod Classic": 50,
    "iPod Mini": 25,
    "Sony Walkman": 25,
    "Sony Discman": 20,
    "Sony MiniDisc": 50,
}


FEE_CONFIG = {
    "consumer_electronics": 0.0935,
    "pro_audio_dj": 0.0935,
    "musical_instruments": 0.1035,
}


DEFAULT_RISK_CONFIG = {
    "packaging": 25.0,
    "pickup_mileage": 15.0,
    "repair_reserve": 125.0,
    "return_reserve": 50.0,
    "required_profit": 200.0,
    "receiver_shipping": 65.0,
    "turntable_shipping": 55.0,
    "small_deck_shipping": 45.0,
    "speaker_shipping": 100.0,
}


@dataclass
class Lead:
    source: str
    title: str
    price: float | None
    url: str
    location: str
    item_id: str = ""
    image_url: str = ""
    review_status: str = ""
    notes: str = ""


@dataclass
class ModelMatch:
    name: str = ""
    brand: str = ""
    category: str = ""
    exact: bool = False
    confidence: int = 0
    reason: str = ""
    price_floor: float = 0.0


@dataclass
class LeadAssessment:
    lead: Lead
    classification: str
    verdict: str
    score: int
    model: ModelMatch
    sold_comp_status: str
    active_context_status: str = "ACTIVE_CONTEXT_OPTIONAL_NOT_USED_FOR_PROFIT"
    reject_reason: str = ""
    interesting: str = ""
    junk_risk: str = ""
    photo_verification: str = ""
    condition_risk: str = ""
    fraud_risk: str = ""
    seller_message: str = ""
    max_buy_price: float | None = None
    underwriting_notes: list[str] = field(default_factory=list)


def normalize_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_price(value: Any) -> float | None:
    text = normalize_space(value).replace("$", "").replace(",", "")
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        price = float(match.group(0))
    except ValueError:
        return None
    if price <= 0:
        return None
    return price


def money(value: float | None) -> str:
    if value is None:
        return "unknown"
    return f"${value:,.0f}"


def contains_term(text: str, term: str) -> bool:
    term = term.lower()
    if " " in term or "-" in term:
        return term in text
    return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text) is not None


def first_matching_term(text: str, terms: list[str]) -> str:
    lowered = text.lower()
    for term in terms:
        if contains_term(lowered, term):
            return term
    return ""


def has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(contains_term(lowered, term) for term in terms)


def canonicalize_model(brand: str, family: str, number: str) -> str:
    brand = brand.strip().title()
    family = family.upper().replace(" ", "-")
    number = number.upper()
    if family:
        return f"{brand} {family}-{number}"
    return f"{brand} {number}"


def detect_exact_model(title: str) -> ModelMatch:
    text = normalize_space(title).lower()
    compact = re.sub(r"[^a-z0-9]", "", text)

    if not text:
        return ModelMatch(reason="No title text")

    direct_patterns = [
        ("McIntosh MA 5100", "mcintosh", "amplifier", [r"\bma[\s-]?5100\b", "ma5100"]),
        ("McIntosh MA 6100", "mcintosh", "amplifier", [r"\bma[\s-]?6100\b", "ma6100"]),
        ("McIntosh C22", "mcintosh", "preamp", [r"\bc[\s-]?22\b", "c22"]),
        ("McIntosh MC 2300", "mcintosh", "power amp", [r"\bmc[\s-]?2300\b", "mc2300"]),
        ("Pioneer SX-1250", "pioneer", "receiver", [r"\bsx[\s-]?1250\b", "sx1250"]),
        ("Pioneer SX-1050", "pioneer", "receiver", [r"\bsx[\s-]?1050\b", "sx1050"]),
        ("Pioneer SX-950", "pioneer", "receiver", [r"\bsx[\s-]?950\b", "sx950"]),
        ("Pioneer SX-850", "pioneer", "receiver", [r"\bsx[\s-]?850\b", "sx850"]),
        ("Pioneer SX-770", "pioneer", "receiver", [r"\bsx[\s-]?770\b", "sx770"]),
        ("Pioneer SX-650", "pioneer", "receiver", [r"\bsx[\s-]?650\b", "sx650"]),
        ("Marantz 2270", "marantz", "receiver", [r"\b2270\b"]),
        ("Marantz 2275", "marantz", "receiver", [r"\b2275\b"]),
        ("Marantz 2245", "marantz", "receiver", [r"\b2245\b"]),
        ("Marantz 2226B", "marantz", "receiver", [r"\b2226b\b", r"\b2226[\s-]?b\b"]),
        ("Sansui G-9000", "sansui", "receiver", [r"\bg[\s-]?9000\b", "g9000"]),
        ("Sansui 9090", "sansui", "receiver", [r"\b9090\b"]),
        ("Technics SA-5370", "technics", "receiver", [r"\bsa[\s-]?5370\b", "sa5370"]),
        ("Technics SL-1200", "technics", "turntable", [r"\bsl[\s-]?1200(?:mk\d+|m\d+)?\b", "sl1200"]),
        ("Technics SL-1210", "technics", "turntable", [r"\bsl[\s-]?1210(?:mk\d+|m\d+)?\b", "sl1210"]),
        ("Technics SL-D35", "technics", "turntable", [r"\bsl[\s-]?d35\b", "sld35"]),
        ("Nakamichi Dragon", "nakamichi", "cassette deck", [r"\bdragon\b"]),
        ("Nakamichi 1000ZXL", "nakamichi", "cassette deck", [r"\b1000[\s-]?zxl\b", "1000zxl"]),
        ("Nakamichi CR-7A", "nakamichi", "cassette deck", [r"\bcr[\s-]?7a\b", "cr7a"]),
        ("Nakamichi ZX-7", "nakamichi", "cassette deck", [r"\bzx[\s-]?7\b", "zx7"]),
        ("Nakamichi ZX-9", "nakamichi", "cassette deck", [r"\bzx[\s-]?9\b", "zx9"]),
        ("Nakamichi BX-300", "nakamichi", "cassette deck", [r"\bbx[\s-]?300\b", "bx300"]),
        ("JBL L100", "jbl", "speakers", [r"\bl[\s-]?100\b", "l100"]),
        ("Realistic STA-82", "realistic", "receiver", [r"\bsta[\s-]?82\b", "sta82"]),
        ("Pioneer PL-600", "pioneer", "turntable", [r"\bpl[\s-]?600\b", "pl600"]),
        ("U-Turn Orbit", "u-turn", "turntable", [r"\borbit\b"]),
        ("Nintendo Wii U", "nintendo", "game console", [r"\bwii[\s-]?u\b", "wiiu"]),
        ("Nintendo Wii", "nintendo", "game console", [r"\bwii\b"]),
        ("Nintendo GameCube", "nintendo", "game console", [r"\bgame[\s-]?cube\b", "gamecube"]),
        ("Nintendo 64", "nintendo", "game console", [r"\bnintendo[\s-]?64\b", r"\bn64\b"]),
        ("Super Nintendo", "nintendo", "game console", [r"\bsuper\s+nintendo\b", r"\bsnes\b"]),
        ("Nintendo NES", "nintendo", "game console", [r"\bnintendo\s+nes\b", r"\bnes\b"]),
        ("Sony PlayStation 2", "sony", "game console", [r"\bplaystation[\s-]?2\b", r"\bps2\b"]),
        ("Sony PlayStation 3", "sony", "game console", [r"\bplaystation[\s-]?3\b", r"\bps3\b"]),
        ("Sega Dreamcast", "sega", "game console", [r"\bdreamcast\b"]),
        ("Sega Genesis", "sega", "game console", [r"\bgenesis\b"]),
        ("Xbox 360", "microsoft", "game console", [r"\bxbox[\s-]?360\b"]),
        ("Original Xbox", "microsoft", "game console", [r"\boriginal\s+xbox\b", r"\bxbox\s+original\b"]),
        ("Apple iMac G3", "apple", "computer", [r"\bimac[\s-]?g3\b"]),
        ("Apple iMac G4", "apple", "computer", [r"\bimac[\s-]?g4\b"]),
        ("Power Mac G4 Cube", "apple", "computer", [r"\bg4\s+cube\b", r"\bpower\s*mac\s*g4\s*cube\b"]),
        ("Apple iMac G5", "apple", "computer", [r"\bimac[\s-]?g5\b"]),
        ("Apple Power Mac G4", "apple", "computer", [r"\bpower\s*mac\s*g4\b"]),
        ("Macintosh Plus", "apple", "computer", [r"\bmacintosh\s+plus\b"]),
        ("Macintosh Classic", "apple", "computer", [r"\bmacintosh\s+classic\b"]),
        ("Macintosh SE", "apple", "computer", [r"\bmacintosh\s+se\b", r"\bmac\s+se\b"]),
        ("Apple II", "apple", "computer", [r"\bapple\s*ii\b", r"\bapple\s*2\b"]),
        ("iPod Classic", "apple", "portable audio", [r"\bipod\s+classic\b"]),
        ("iPod Mini", "apple", "portable audio", [r"\bipod\s+mini\b"]),
        ("Sony Walkman", "sony", "portable audio", [r"\bwalkman\b"]),
        ("Sony Discman", "sony", "portable audio", [r"\bdiscman\b"]),
        ("Sony MiniDisc", "sony", "portable audio", [r"\bminidisc\b", r"\bmini\s+disc\b"]),
    ]

    for model_name, brand, category, patterns in direct_patterns:
        brand_present = brand in text or brand in compact
        for pattern in patterns:
            matched = re.search(pattern, text) is not None if pattern.startswith(r"\b") else pattern in compact
            if matched and (
                brand_present
                or brand in ["pioneer", "technics", "nakamichi", "nintendo", "sega", "microsoft", "apple", "sony"]
            ):
                return ModelMatch(
                    name=model_name,
                    brand=brand.title(),
                    category=category,
                    exact=True,
                    confidence=95 if brand_present else 85,
                    reason=f"Exact model token matched: {model_name}",
                    price_floor=MODEL_PRICE_FLOORS.get(model_name, 0.0),
                )

    hk_match = re.search(r"\bh[ao]rm[ao]n\s+k[ao]rd[ao]n\s+hk[\s-]?([a-z0-9]+)\b", text)
    if hk_match:
        name = f"Harman Kardon HK-{hk_match.group(1).upper()}"
        return ModelMatch(
            name=name,
            brand="Harman Kardon",
            category="receiver",
            exact=True,
            confidence=80,
            reason=f"Exact family/model number detected: {name}",
            price_floor=MODEL_PRICE_FLOORS.get(name, 0.0),
        )

    # Generic model families. These are useful for photo queues, not valuation.
    family_patterns = [
        ("Pioneer", "SX", r"\bsx[\s-]?([0-9]{3,4})\b", "receiver"),
        ("Pioneer", "SA", r"\bsa[\s-]?([0-9]{3,4})\b", "amplifier"),
        ("Pioneer", "TX", r"\btx[\s-]?([0-9]{3,4})\b", "tuner"),
        ("Marantz", "", r"\b(22[0-9]{2}|23[0-9]{2}|10[0-9]{2}|11[0-9]{2})\b", "receiver"),
        ("Technics", "SA", r"\bsa[\s-]?([0-9]{3,4})\b", "receiver"),
        ("Sansui", "AU", r"\bau[\s-]?([0-9]{3,4})\b", "amplifier"),
        ("Sansui", "G", r"\bg[\s-]?([0-9]{3,4})\b", "receiver"),
        ("Yamaha", "CR", r"\bcr[\s-]?([0-9]{3,4})\b", "receiver"),
        ("Yamaha", "CA", r"\bca[\s-]?([0-9]{3,4})\b", "amplifier"),
        ("Sony", "STR", r"\bstr[\s-]?([a-z0-9-]+)\b", "receiver"),
        ("Kenwood", "KR", r"\bkr[\s-]?([0-9]{3,4})\b", "receiver"),
        ("Realistic", "STA", r"\bsta[\s-]?([0-9]{2,4})\b", "receiver"),
        ("Pioneer", "PL", r"\bpl[\s-]?([0-9]{2,4})\b", "turntable"),
        ("Technics", "SL-D", r"\bsl[\s-]?d([0-9]{1,3})\b", "turntable"),
    ]

    for brand, family, pattern, category in family_patterns:
        if brand.lower() not in text:
            continue
        match = re.search(pattern, text)
        if match:
            name = canonicalize_model(brand, family, match.group(1))
            return ModelMatch(
                name=name,
                brand=brand,
                category=category,
                exact=True,
                confidence=80,
                reason=f"Exact family/model number detected: {name}",
                price_floor=MODEL_PRICE_FLOORS.get(name, 0.0),
            )

    brand = next((b for b in BRANDS if contains_term(text, b)), "")
    category = detect_equipment_category(title)
    if brand and category:
        return ModelMatch(
            name=f"{brand.title()} {category} (model unknown)",
            brand=brand.title(),
            category=category,
            exact=False,
            confidence=45,
            reason="Brand and equipment type detected, but no exact model number",
            price_floor=0.0,
        )

    if brand:
        return ModelMatch(
            name=f"{brand.title()} (model unknown)",
            brand=brand.title(),
            category="unknown",
            exact=False,
            confidence=25,
            reason="Brand detected, but no equipment type or model number",
            price_floor=0.0,
        )

    return ModelMatch(reason="No brand/model pattern detected")


def detect_equipment_category(title: str) -> str:
    text = title.lower()
    if any(term in text for term in ["turntable", "record player", "sl-1200", "sl 1200"]):
        return "turntable"
    if any(term in text for term in ["console", "gamecube", "nintendo", "playstation", "xbox", "dreamcast", "genesis", " wii"]):
        return "game console"
    if any(term in text for term in ["macintosh", "imac", "power mac", "apple ii", "vintage computer"]):
        return "computer"
    if any(term in text for term in ["ipod", "walkman", "discman", "minidisc", "mini disc"]):
        return "portable audio"
    if any(term in text for term in ["receiver", "am/fm"]):
        return "receiver"
    if any(term in text for term in ["integrated amplifier", "amplifier", "power amp", " amp"]):
        return "amplifier"
    if any(term in text for term in ["cassette deck", "tape deck", "deck"]):
        return "cassette deck"
    if "speaker" in text:
        return "speakers"
    if "tuner" in text:
        return "tuner"
    if "preamp" in text or "preamplifier" in text:
        return "preamp"
    if "equalizer" in text or " eq" in text:
        return "equalizer"
    if "cd player" in text:
        return "cd player"
    if "stereo" in text:
        return "stereo equipment"
    return ""


def load_all_leads() -> list[Lead]:
    leads: list[Lead] = []

    if MERCARI_CSV.exists():
        with MERCARI_CSV.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                price = parse_price(row.get("price_usd"))
                if price is None:
                    cents = parse_price(row.get("price_cents"))
                    price = cents / 100 if cents is not None else None
                leads.append(
                    Lead(
                        source="Mercari",
                        title=normalize_space(row.get("title")),
                        price=price,
                        url=normalize_space(row.get("listing_url") or row.get("url")),
                        location="Online",
                        item_id=normalize_space(row.get("item_id")),
                        image_url=normalize_space(row.get("image_url")),
                        review_status=normalize_space(row.get("review_status")),
                        notes=normalize_space(row.get("notes")),
                    )
                )

    if FACEBOOK_CSV.exists():
        with FACEBOOK_CSV.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                leads.append(
                    Lead(
                        source="Facebook Marketplace",
                        title=normalize_space(row.get("title")),
                        price=parse_price(row.get("price")),
                        url=normalize_space(row.get("listing_url") or row.get("url")),
                        location=normalize_space(row.get("location")),
                        item_id=normalize_space(row.get("listing_url") or row.get("item_id")),
                        image_url=normalize_space(row.get("photo_url") or row.get("image_url")),
                        review_status=normalize_space(row.get("review_status")),
                        notes=normalize_space(row.get("notes")),
                    )
                )

    return dedupe_leads(leads)


def dedupe_leads(leads: list[Lead]) -> list[Lead]:
    seen: set[str] = set()
    unique: list[Lead] = []
    for lead in leads:
        key = lead.url or lead.item_id or f"{lead.source}:{lead.title}:{lead.price}"
        key = key.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(lead)
    return unique


def lead_sort_key(assessment: LeadAssessment) -> tuple[int, int, float, int, float]:
    price = assessment.lead.price if assessment.lead.price is not None else 999999.0
    verdict_rank = {"INVESTIGATE": 3, "WATCH": 2, "SKIP": 1}.get(assessment.verdict, 0)
    spread = -999999.0
    if assessment.max_buy_price is not None and assessment.lead.price is not None:
        spread = assessment.max_buy_price - assessment.lead.price
    confirmed_margin = 1 if spread > 0 else 0
    return (verdict_rank, confirmed_margin, spread, assessment.score, -price)


def assess_lead(lead: Lead, sold_comp_index: dict[str, dict[str, Any]] | None = None) -> LeadAssessment:
    sold_comp_index = sold_comp_index or {}
    title = lead.title
    text = title.lower()
    price = lead.price

    model = detect_exact_model(title)
    reject = first_matching_term(title, HARD_REJECT_TERMS)
    modern_av = first_matching_term(title, MODERN_AV_TERMS)
    equipment_category = detect_equipment_category(title)
    full_unit_signal = bool(equipment_category) or has_any(title, POSITIVE_CONDITION_TERMS)
    positive_condition = has_any(title, POSITIVE_CONDITION_TERMS)
    negative_condition = has_any(title, NEGATIVE_CONDITION_TERMS)

    classification = "UNKNOWN"
    verdict = "SKIP"
    score = 0
    reject_reason = ""
    interesting = ""
    junk_risk = ""
    photo_verification = ""
    condition_risk = ""
    fraud_risk = ""
    underwriting_notes: list[str] = []

    if reject:
        classification = "SKIP"
        reject_reason = f"Hard reject term in title: {reject}"
        junk_risk = "Likely parts/accessory/apparel/manual rather than a complete unit."
    elif modern_av:
        classification = "SKIP"
        reject_reason = f"Modern AV/home-theater term in title: {modern_av}"
        junk_risk = "Modern home-theater receivers are outside the current vintage stereo target lane."
    elif price is None:
        classification = "NEEDS_MANUAL_REVIEW"
        verdict = "WATCH"
        score = 20
        reject_reason = "Missing or unparseable asking price"
    elif price < 20:
        classification = "SKIP"
        reject_reason = "Too cheap to trust as complete equipment without strong proof"
        junk_risk = "Could be a small accessory, part, or stale/noisy scrape result."
    elif model.exact and full_unit_signal:
        classification = "NEEDS_SOLD_COMPS"
        verdict = "INVESTIGATE"
        score = 70
        interesting = f"Exact model detected: {model.name}."
        photo_verification = f"Confirm full unit: {verification_target(model)}."
    elif model.exact:
        classification = "NEEDS_PHOTO_CHECK"
        verdict = "WATCH"
        score = 55
        interesting = f"Exact model token appears in title: {model.name}."
        junk_risk = "Title does not clearly prove it is a complete working unit."
        photo_verification = "Open listing photos before seller contact; verify complete equipment, not a case, manual, or part."
    elif model.brand and equipment_category:
        classification = "NEEDS_EXACT_MODEL"
        verdict = "WATCH"
        score = 40
        interesting = f"{model.brand} {equipment_category} may be relevant."
        junk_risk = "Generic title could be a low-value model or unrelated modern equipment."
        photo_verification = "Find exact model number on front panel, back panel, or serial/model plate."
    elif has_any(title, EQUIPMENT_TERMS):
        classification = "NEEDS_EXACT_MODEL"
        verdict = "WATCH"
        score = 25
        interesting = "Looks like resale-relevant equipment, but no target brand/model is visible."
        junk_risk = "No brand/model means value cannot be assessed."
        photo_verification = "Look for brand and exact model number before any pricing work."
    else:
        classification = "SKIP"
        reject_reason = "No usable equipment/model signal"
        junk_risk = "Not enough evidence that this is resale-relevant equipment."

    if lead.source == "Facebook Marketplace" and verdict != "SKIP":
        score += 10
        fraud_risk = "Local listing: verify in person; watch for deposit/shipping requests."
    elif lead.source == "Mercari" and verdict != "SKIP":
        score -= 5
        fraud_risk = "Shipped marketplace item: no in-person test; return/condition risk is higher."

    if positive_condition and verdict != "SKIP":
        score += 10
    if negative_condition:
        score -= 25
        condition_risk = "Title contains repair/untested/as-is language; reserve more repair risk or skip."
    elif verdict != "SKIP":
        condition_risk = "Condition not proven until photos, seller answers, or in-person test confirm it."

    if lead.image_url and verdict != "SKIP":
        score += 5
    elif verdict != "SKIP":
        score -= 5
        photo_verification = photo_verification or "No photo URL in normalized data; open listing manually."

    if price is not None and model.price_floor:
        if price < model.price_floor * 0.25:
            score -= 10
            underwriting_notes.append("Very low ask for this model family; verify it is not parts, scam, or broken.")
        elif price <= model.price_floor:
            score += 10
            underwriting_notes.append("Ask is below conservative category floor, worth checking once full-unit status is proven.")
        elif price > model.price_floor * 3 and model.exact:
            score -= 25
            underwriting_notes.append("Ask is high versus the conservative triage floor; watch until sold comps prove room.")
    elif price is not None and model.exact:
        if price > 1500:
            score -= 40
            underwriting_notes.append("High ask on a model without configured pricing; keep out of immediate review until sold comps are attached.")
        elif price > 750:
            score -= 20
            underwriting_notes.append("Ask is not obviously cheap for an unpriced exact model; sold comps required before seller action.")

    if model.category == "tuner" and verdict != "SKIP":
        score = min(score, 60)
        verdict = "WATCH"
        underwriting_notes.append("Tuners are lower-priority context items unless a specific sold-comp case proves upside.")

    sold_status = "NEEDS_SOLD_COMPS"
    max_buy = None
    if model.exact:
        comp_summary = sold_comp_index.get(model.name)
        if comp_summary and comp_summary.get("valid_full_unit_count", 0) >= 3:
            low_sold = float(comp_summary.get("low_sold") or 0)
            high_sold = float(comp_summary.get("high_sold") or 0)
            price_spread_ratio = high_sold / low_sold if low_sold > 0 else 999.0
            if price_spread_ratio > 3.0:
                sold_status = "LOW_CONFIDENCE_SOLD_COMPS"
                underwriting_notes.append(
                    f"Sold comps are too dispersed for confident underwriting: {money(low_sold)} - {money(high_sold)}."
                )
            else:
                sold_status = "VALID_SOLD_COMPS_ATTACHED"
                max_buy = calculate_max_buy_price(model, comp_summary)
                underwriting_notes.append(
                    f"Clean sold comps available: {comp_summary['valid_full_unit_count']} valid full-unit sales."
                )
                if price is not None:
                    spread = max_buy - price
                    if spread <= 0:
                        score -= 35
                        if verdict == "INVESTIGATE":
                            verdict = "WATCH"
                        underwriting_notes.append(
                            "Clean sold comps do not support resale arbitrage at the current ask after configured fees/reserves."
                        )
                    elif spread < max(25.0, price * 0.15):
                        score -= 10
                        underwriting_notes.append(
                            "Clean sold comps show only thin room; verify condition and negotiate before treating it as actionable."
                        )
                    else:
                        score += 15
                        underwriting_notes.append("Clean sold comps support room above the current ask after configured fees/reserves.")
        elif comp_summary:
            sold_status = "LOW_CONFIDENCE_SOLD_COMPS"
            underwriting_notes.append(
                "Sold comps exist, but fewer than 3 valid full-unit comps survived cleaning."
            )
    else:
        sold_status = "BLOCKED_NEEDS_EXACT_MODEL"

    score = max(0, min(100, score))
    if score < 35 and verdict != "SKIP":
        verdict = "WATCH"
    if classification == "SKIP":
        verdict = "SKIP"
        score = min(score, 10)
        sold_status = "NOT_APPLICABLE_SKIP"

    seller_message = generate_seller_message(lead, model, classification)

    return LeadAssessment(
        lead=lead,
        classification=classification,
        verdict=verdict,
        score=score,
        model=model,
        sold_comp_status=sold_status,
        reject_reason=reject_reason,
        interesting=interesting or "No specific upside identified yet.",
        junk_risk=junk_risk or "Could still be incomplete, mis-modeled, non-working, or overpriced.",
        photo_verification=photo_verification or "Verify exact model, full-unit status, condition, and back-panel label.",
        condition_risk=condition_risk or "Unknown condition until tested.",
        fraud_risk=fraud_risk or "Normal marketplace risk; do not prepay outside platform protections.",
        seller_message=seller_message,
        max_buy_price=max_buy,
        underwriting_notes=underwriting_notes,
    )


def verification_target(model: ModelMatch) -> str:
    if model.category == "game console":
        return "console body, cables, controllers, games/accessories, model label, and proof it reads a disc or cartridge"
    if model.category == "computer":
        return "front, back model label, screen/monitor, keyboard/mouse/cables, and a photo showing it booted"
    if model.category == "portable audio":
        return "front, back, battery compartment, charger/cable, and proof playback/output works"
    return "front panel, back panel label, all knobs/buttons, and no obvious damage"


def test_question(model: ModelMatch) -> str:
    if model.category == "game console":
        return "Does it power on, show video on a TV, and read a game? Are the power/video cables and controllers included?"
    if model.category == "computer":
        return "Does it power on and boot? Are the screen, keyboard, mouse, and power cable included, and are there cracks or display issues?"
    if model.category == "portable audio":
        return "Does it power on and play audio through headphones or line out? Any battery corrosion or missing charger/cable?"
    return "Does it power on and play through both channels? Any scratchy controls, hum, dead inputs, or missing knobs?"


def generate_seller_message(lead: Lead, model: ModelMatch, classification: str) -> str:
    item_name = model.name if model.name else "the item"
    photo_target = verification_target(model)
    if classification == "NEEDS_EXACT_MODEL":
        return (
            f"Hi, is {lead.title[:80]} still available? Could you send a clear photo of the "
            "model number plate or label? I am trying to confirm the exact model "
            "and whether it is complete before I come look."
        )
    if classification == "NEEDS_PHOTO_CHECK":
        return (
            f"Hi, is the {item_name} still available? Can you confirm this is the complete unit, not just "
            f"a part/manual/accessory, and send clear photos of the {photo_target}?"
        )
    if classification == "NEEDS_SOLD_COMPS":
        return (
            f"Hi, is the {item_name} still available? {test_question(model)} If local, I would want to test it "
            "briefly before deciding."
        )
    return "No seller message recommended for this lead."


def load_clean_sold_comp_index(path: Path = CLEAN_SOLD_COMPS_CSV) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    by_model: dict[str, list[float]] = {}
    counts: dict[str, int] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("comp_classification") != "FULL_UNIT":
                continue
            model = row.get("model") or ""
            price = parse_price(row.get("sold_price"))
            if not model or price is None:
                continue
            by_model.setdefault(model, []).append(price)
            counts[model] = counts.get(model, 0) + 1

    index: dict[str, dict[str, Any]] = {}
    for model, prices in by_model.items():
        prices.sort()
        index[model] = {
            "valid_full_unit_count": len(prices),
            "median_sold": median(prices),
            "low_sold": prices[0],
            "high_sold": prices[-1],
        }
    return index


def category_fee_rate(model: ModelMatch) -> float:
    if model.category in ["turntable", "cassette deck", "speakers"]:
        return FEE_CONFIG["musical_instruments"]
    return FEE_CONFIG["consumer_electronics"]


def estimated_shipping(model: ModelMatch) -> float:
    if model.category == "game console":
        return 25.0
    if model.category == "portable audio":
        return 15.0
    if model.category == "computer":
        return 60.0
    if model.category == "turntable":
        return DEFAULT_RISK_CONFIG["turntable_shipping"]
    if model.category in ["receiver", "amplifier", "power amp"]:
        return DEFAULT_RISK_CONFIG["receiver_shipping"]
    if model.category in ["cassette deck", "tuner", "preamp", "equalizer", "cd player"]:
        return DEFAULT_RISK_CONFIG["small_deck_shipping"]
    if model.category == "speakers":
        return DEFAULT_RISK_CONFIG["speaker_shipping"]
    return DEFAULT_RISK_CONFIG["small_deck_shipping"]


def underwriting_reserves(model: ModelMatch) -> dict[str, float]:
    if model.category == "game console":
        return {"packaging": 12.0, "pickup_mileage": 10.0, "repair_reserve": 25.0, "return_reserve": 20.0, "required_profit": 50.0}
    if model.category == "portable audio":
        return {"packaging": 8.0, "pickup_mileage": 10.0, "repair_reserve": 20.0, "return_reserve": 15.0, "required_profit": 40.0}
    if model.category == "computer":
        return {"packaging": 30.0, "pickup_mileage": 15.0, "repair_reserve": 100.0, "return_reserve": 50.0, "required_profit": 150.0}
    return {
        "packaging": DEFAULT_RISK_CONFIG["packaging"],
        "pickup_mileage": DEFAULT_RISK_CONFIG["pickup_mileage"],
        "repair_reserve": DEFAULT_RISK_CONFIG["repair_reserve"],
        "return_reserve": DEFAULT_RISK_CONFIG["return_reserve"],
        "required_profit": DEFAULT_RISK_CONFIG["required_profit"],
    }


def calculate_max_buy_price(model: ModelMatch, comp_summary: dict[str, Any]) -> float:
    resale = float(comp_summary["median_sold"])
    fees = resale * category_fee_rate(model)
    reserves = underwriting_reserves(model)
    costs = (
        fees
        + estimated_shipping(model)
        + reserves["packaging"]
        + reserves["pickup_mileage"]
        + reserves["repair_reserve"]
        + reserves["return_reserve"]
        + reserves["required_profit"]
    )
    return max(0.0, resale - costs)
