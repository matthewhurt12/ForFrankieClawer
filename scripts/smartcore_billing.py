#!/usr/bin/env python3
"""
SmartCore billing generator.

Creates local invoice PDFs, HTML previews, and email draft packages from
config/smartcore_billing.json. This script never sends email.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from email.message import EmailMessage
from email.utils import formatdate
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "smartcore_billing.json"
LEDGER_NAME = "invoice_ledger.csv"

TEAL = (0.0, 0.67, 0.69)
DARK = (0.04, 0.08, 0.13)
MUTED = (0.35, 0.40, 0.46)
LINE = (0.82, 0.86, 0.90)
WHITE = (1, 1, 1)


@dataclass
class Invoice:
    number: int
    invoice_date: date
    due_date: date
    service_month: date
    service_key: str
    email_group: str
    client_key: str
    client: dict[str, Any]
    company: dict[str, Any]
    line_items: list[dict[str, Any]]
    note: str
    subtotal: Decimal
    total: Decimal
    slug: str


def money(value: Any) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt_money(value: Decimal) -> str:
    return f"${value:,.2f}"


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_month(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m").date().replace(day=1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Expected YYYY-MM, got {value!r}") from exc


def add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    last_day = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    return date(year, month, min(day.day, last_day))


def month_name(month: date) -> str:
    return month.strftime("%B")


def month_label(month: date) -> str:
    return month.strftime("%B %Y")


def months_sentence(months: list[date]) -> str:
    names = [month_name(item) for item in months]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def safe_slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower())
    return value.strip("_") or "invoice"


def read_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def invoice_total(items: list[dict[str, Any]]) -> Decimal:
    total = Decimal("0.00")
    for item in items:
        total += money(item["quantity"]) * money(item["unit_price"])
    return total.quantize(Decimal("0.01"))


def build_invoices(config: dict[str, Any], invoice_date: date, service_months: list[date], start_number: int) -> list[Invoice]:
    invoices: list[Invoice] = []
    number = start_number
    due_date = add_months(invoice_date, 1)
    for recurring in config["recurring_invoices"]:
        client_key = recurring["client"]
        client = config["clients"][client_key]
        client_slug = safe_slug(client["company"])
        for service_month in service_months:
            note = recurring["note_template"].format(
                service_month_name=month_name(service_month),
                service_month_year=month_label(service_month),
                service_year=service_month.year,
            )
            total = invoice_total(recurring["line_items"])
            invoices.append(
                Invoice(
                    number=number,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    service_month=service_month,
                    service_key=recurring["key"],
                    email_group=recurring["email_group"],
                    client_key=client_key,
                    client=client,
                    company=config["company"],
                    line_items=recurring["line_items"],
                    note=note,
                    subtotal=total,
                    total=total,
                    slug=config["invoice"]["filename_template"].format(
                        number=number,
                        client_slug=client_slug,
                        service_month_name=month_name(service_month),
                        service_year=service_month.year,
                    ),
                )
            )
            number += 1
    return invoices


def invoice_filename(invoice: Invoice, suffix: str) -> str:
    return f"{invoice.slug}.{suffix}"


def client_block(client: dict[str, Any]) -> str:
    lines = [client.get("company", ""), client.get("contact", "")]
    lines.extend(client.get("address_lines", []))
    if client.get("phone"):
        lines.append(client["phone"])
    if client.get("email"):
        lines.append(client["email"])
    return "\n".join(line for line in lines if line)


def company_block(company: dict[str, Any]) -> str:
    lines = [company.get("name", "")]
    lines.extend(company.get("address_lines", []))
    if company.get("phone"):
        lines.append(company["phone"])
    if company.get("billing_email"):
        lines.append(company["billing_email"])
    return "\n".join(line for line in lines if line)


def html_invoice(invoice: Invoice) -> str:
    rows = []
    for item in invoice.line_items:
        qty = money(item["quantity"])
        unit_price = money(item["unit_price"])
        amount = qty * unit_price
        rows.append(
            f"""
            <tr>
              <td><strong>{html.escape(item['name'])}</strong><br><span>{html.escape(item.get('description', ''))}</span></td>
              <td>{qty.normalize()}</td>
              <td>{fmt_money(unit_price)}</td>
              <td>{fmt_money(amount)}</td>
            </tr>
            """
        )
    logo = html.escape(str(Path(invoice.company["logo_path"]).as_posix()))
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>SmartCore Solutions Invoice #{invoice.number}</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: #0b1320; margin: 42px; }}
    .top {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #14b8bb; padding-bottom: 22px; }}
    .logo {{ max-width: 260px; height: auto; }}
    h1 {{ margin: 0; font-size: 34px; letter-spacing: 2px; }}
    .muted {{ color: #64707d; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 34px; margin-top: 28px; }}
    .label {{ color: #14aeb2; font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: .08em; }}
    .summary td {{ padding: 4px 0 4px 22px; }}
    table.items {{ width: 100%; border-collapse: collapse; margin-top: 34px; }}
    table.items th {{ text-align: left; border-bottom: 2px solid #d4dbe2; padding: 10px 8px; color: #52606d; font-size: 12px; text-transform: uppercase; }}
    table.items td {{ border-bottom: 1px solid #e7ebef; padding: 13px 8px; vertical-align: top; }}
    table.items td:nth-child(n+2), table.items th:nth-child(n+2) {{ text-align: right; }}
    table.items span {{ color: #64707d; }}
    .totals {{ width: 280px; margin-left: auto; margin-top: 18px; }}
    .totals td {{ padding: 7px 0; }}
    .totals td:last-child {{ text-align: right; font-weight: 700; }}
    .due {{ color: #0b1320; font-size: 18px; }}
    .notes {{ margin-top: 40px; border-top: 1px solid #e7ebef; padding-top: 18px; }}
  </style>
</head>
<body>
  <div class="top">
    <div><img class="logo" src="{logo}" alt="SmartCore Solutions"></div>
    <div style="text-align:right">
      <h1>INVOICE</h1>
      <div class="muted">{html.escape(company_block(invoice.company)).replace(chr(10), '<br>')}</div>
    </div>
  </div>
  <div class="grid">
    <div>
      <div class="label">Bill To</div>
      <p>{html.escape(client_block(invoice.client)).replace(chr(10), '<br>')}</p>
    </div>
    <div>
      <table class="summary">
        <tr><td class="muted">Invoice Number:</td><td><strong>{invoice.number}</strong></td></tr>
        <tr><td class="muted">Invoice Date:</td><td>{invoice.invoice_date.strftime('%B %-d, %Y') if sys.platform != 'win32' else invoice.invoice_date.strftime('%B %#d, %Y')}</td></tr>
        <tr><td class="muted">Payment Due:</td><td>{invoice.due_date.strftime('%B %-d, %Y') if sys.platform != 'win32' else invoice.due_date.strftime('%B %#d, %Y')}</td></tr>
        <tr><td class="muted">Amount Due (USD):</td><td class="due"><strong>{fmt_money(invoice.total)}</strong></td></tr>
      </table>
    </div>
  </div>
  <table class="items">
    <thead><tr><th>Items</th><th>Quantity</th><th>Price</th><th>Amount</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <table class="totals">
    <tr><td>Total:</td><td>{fmt_money(invoice.total)}</td></tr>
    <tr><td>Amount Due (USD):</td><td>{fmt_money(invoice.total)}</td></tr>
  </table>
  <div class="notes">
    <div class="label">Notes / Terms</div>
    <p>{html.escape(invoice.note)}</p>
  </div>
</body>
</html>
"""


def write_html(invoice: Invoice, path: Path) -> None:
    path.write_text(html_invoice(invoice), encoding="utf-8")


def draw_text(page: fitz.Page, rect: fitz.Rect, text: str, size: float = 10, color: tuple[float, float, float] = DARK, align: int = fitz.TEXT_ALIGN_LEFT, bold: bool = False) -> None:
    # Use the built-in Helvetica alias. Some PyMuPDF installs do not expose a
    # portable bold alias without an external font file.
    result = page.insert_textbox(
        rect,
        text,
        fontsize=size,
        fontname="helv",
        color=color,
        align=align,
    )
    if result >= 0:
        return

    # Fallback for strict textbox fitting: draw line by line so important
    # invoice metadata never silently disappears.
    line_height = size * 1.25
    lines = text.splitlines() or [text]
    y = rect.y0 + size
    for line in lines:
        if y > rect.y1:
            break
        if align == fitz.TEXT_ALIGN_RIGHT:
            text_width = fitz.get_text_length(line, fontname="helv", fontsize=size)
            x = rect.x1 - text_width
        elif align == fitz.TEXT_ALIGN_CENTER:
            text_width = fitz.get_text_length(line, fontname="helv", fontsize=size)
            x = rect.x0 + max(0, (rect.width - text_width) / 2)
        else:
            x = rect.x0
        page.insert_text((x, y), line, fontsize=size, fontname="helv", color=color)
        y += line_height


def draw_invoice_pdf(invoice: Invoice, path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    margin = 54

    logo_path = ROOT / invoice.company["logo_path"]
    if logo_path.exists():
        page.insert_image(fitz.Rect(margin, 45, margin + 210, 108), filename=str(logo_path), keep_proportion=True)
    else:
        draw_text(page, fitz.Rect(margin, 45, margin + 260, 80), invoice.company["name"], size=19, color=TEAL, bold=True)

    draw_text(page, fitz.Rect(350, 45, 558, 88), "INVOICE", size=30, align=fitz.TEXT_ALIGN_RIGHT, bold=True)
    draw_text(page, fitz.Rect(340, 92, 558, 148), company_block(invoice.company), size=8.5, color=MUTED, align=fitz.TEXT_ALIGN_RIGHT)
    page.draw_line((margin, 156), (558, 156), color=TEAL, width=2)

    draw_text(page, fitz.Rect(margin, 184, 230, 201), "BILL TO", size=9, color=TEAL, bold=True)
    draw_text(page, fitz.Rect(margin, 205, 280, 302), client_block(invoice.client), size=10)

    labels = ["Invoice Number:", "Invoice Date:", "Payment Due:", "Amount Due (USD):"]
    values = [
        str(invoice.number),
        invoice.invoice_date.strftime("%B %#d, %Y" if sys.platform == "win32" else "%B %-d, %Y"),
        invoice.due_date.strftime("%B %#d, %Y" if sys.platform == "win32" else "%B %-d, %Y"),
        fmt_money(invoice.total),
    ]
    y = 185
    for label, value in zip(labels, values):
        draw_text(page, fitz.Rect(326, y, 450, y + 18), label, size=9, color=MUTED, align=fitz.TEXT_ALIGN_RIGHT)
        draw_text(page, fitz.Rect(462, y, 558, y + 18), value, size=10, align=fitz.TEXT_ALIGN_RIGHT, bold=label.startswith("Amount"))
        y += 24

    table_top = 328
    page.draw_rect(fitz.Rect(margin, table_top, 558, table_top + 28), color=LINE, fill=(0.95, 0.97, 0.98), width=0.5)
    draw_text(page, fitz.Rect(64, table_top + 8, 305, table_top + 24), "Items", size=8, color=MUTED, bold=True)
    draw_text(page, fitz.Rect(330, table_top + 8, 388, table_top + 24), "Quantity", size=8, color=MUTED, align=fitz.TEXT_ALIGN_RIGHT, bold=True)
    draw_text(page, fitz.Rect(412, table_top + 8, 474, table_top + 24), "Price", size=8, color=MUTED, align=fitz.TEXT_ALIGN_RIGHT, bold=True)
    draw_text(page, fitz.Rect(492, table_top + 8, 548, table_top + 24), "Amount", size=8, color=MUTED, align=fitz.TEXT_ALIGN_RIGHT, bold=True)

    y = table_top + 42
    for item in invoice.line_items:
        qty = money(item["quantity"])
        price = money(item["unit_price"])
        amount = qty * price
        row_bottom = y + 45
        page.draw_line((margin, row_bottom), (558, row_bottom), color=LINE, width=0.5)
        draw_text(page, fitz.Rect(64, y, 305, y + 18), item["name"], size=10, bold=True)
        draw_text(page, fitz.Rect(64, y + 16, 305, y + 36), item.get("description", ""), size=9, color=MUTED)
        draw_text(page, fitz.Rect(330, y, 388, y + 18), f"{qty.normalize()}", size=10, align=fitz.TEXT_ALIGN_RIGHT)
        draw_text(page, fitz.Rect(412, y, 474, y + 18), fmt_money(price), size=10, align=fitz.TEXT_ALIGN_RIGHT)
        draw_text(page, fitz.Rect(492, y, 548, y + 18), fmt_money(amount), size=10, align=fitz.TEXT_ALIGN_RIGHT)
        y += 52

    totals_top = y + 15
    draw_text(page, fitz.Rect(360, totals_top, 466, totals_top + 20), "Total:", size=11, align=fitz.TEXT_ALIGN_RIGHT)
    draw_text(page, fitz.Rect(476, totals_top, 558, totals_top + 20), fmt_money(invoice.total), size=11, align=fitz.TEXT_ALIGN_RIGHT, bold=True)
    draw_text(page, fitz.Rect(330, totals_top + 30, 466, totals_top + 52), "Amount Due (USD):", size=11, align=fitz.TEXT_ALIGN_RIGHT, bold=True)
    draw_text(page, fitz.Rect(476, totals_top + 30, 558, totals_top + 52), fmt_money(invoice.total), size=11, align=fitz.TEXT_ALIGN_RIGHT, bold=True)

    notes_top = totals_top + 95
    page.draw_line((margin, notes_top), (558, notes_top), color=LINE, width=0.5)
    draw_text(page, fitz.Rect(margin, notes_top + 18, 220, notes_top + 34), "NOTES / TERMS", size=9, color=TEAL, bold=True)
    draw_text(page, fitz.Rect(margin, notes_top + 42, 558, notes_top + 86), invoice.note, size=10)

    footer = f"{invoice.company['name']} | {invoice.company.get('billing_email', '')}"
    draw_text(page, fitz.Rect(margin, 742, 558, 760), footer, size=8, color=MUTED, align=fitz.TEXT_ALIGN_CENTER)

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


def invoice_output_dir(config: dict[str, Any], invoice_date: date) -> Path:
    return ROOT / config["invoice"]["output_dir"] / invoice_date.isoformat()


def write_ledger(invoices: list[Invoice], output_dir: Path, pdf_paths: dict[int, Path]) -> None:
    ledger = output_dir / LEDGER_NAME
    with ledger.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "invoice_number",
                "invoice_date",
                "due_date",
                "service_month",
                "client",
                "email_group",
                "total",
                "pdf_path",
            ],
        )
        writer.writeheader()
        for invoice in invoices:
            writer.writerow(
                {
                    "invoice_number": invoice.number,
                    "invoice_date": invoice.invoice_date.isoformat(),
                    "due_date": invoice.due_date.isoformat(),
                    "service_month": invoice.service_month.isoformat(),
                    "client": invoice.client["company"],
                    "email_group": invoice.email_group,
                    "total": f"{invoice.total:.2f}",
                    "pdf_path": str(pdf_paths[invoice.number].relative_to(ROOT)),
                }
            )


def invoice_numbers_label(invoices: list[Invoice]) -> str:
    numbers = [str(invoice.number) for invoice in invoices]
    if len(numbers) == 1:
        return numbers[0]
    if len(numbers) == 2:
        return f"{numbers[0]} & {numbers[1]}"
    return f"{', '.join(numbers[:-1])} & {numbers[-1]}"


def email_body(service_label: str, months: list[date], transition_note: bool) -> str:
    month_text = months_sentence(months)
    plural = "months" if len(months) > 1 else "month"
    lines = [
        f"Attached is the {service_label} service bill for the {plural} of {month_text}.",
        "",
    ]
    if transition_note:
        lines.extend(
            [
                "Please note, billing@smartcorefleet.com will be used for SmartCore Solutions billing communications going forward.",
                "",
            ]
        )
    lines.extend(["Let me know if you have any questions.", "", "Thanks,"])
    return "\n".join(lines)


def write_email_drafts(config: dict[str, Any], invoices: list[Invoice], output_dir: Path, pdf_paths: dict[int, Path], transition_note: bool) -> None:
    drafts_dir = output_dir / "email_drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[Invoice]] = {}
    for invoice in invoices:
        groups.setdefault(invoice.email_group, []).append(invoice)

    sender = config["company"].get("billing_email", "")
    for group_key, group_invoices in groups.items():
        group_config = config["email_groups"][group_key]
        group_invoices = sorted(group_invoices, key=lambda invoice: invoice.number)
        months = sorted({invoice.service_month for invoice in group_invoices})
        number_label = invoice_numbers_label(group_invoices)
        subject = group_config["subject_template"].format(invoice_numbers=number_label)
        body = email_body(group_config["service_label"], months, transition_note=transition_note)
        attachment_paths = [pdf_paths[invoice.number] for invoice in group_invoices]

        slug = safe_slug(subject)
        txt_path = drafts_dir / f"{slug}.txt"
        lines = [
            f"From: {sender}",
            f"To: {', '.join(group_config.get('to', []))}",
            f"Subject: {subject}",
            "",
            body,
            "",
            "Attachments:",
        ]
        if group_config.get("cc"):
            lines.insert(2, f"Cc: {', '.join(group_config['cc'])}")
        lines.extend(f"- {path}" for path in attachment_paths)
        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        message = EmailMessage()
        message["From"] = sender
        message["To"] = ", ".join(group_config.get("to", []))
        if group_config.get("cc"):
            message["Cc"] = ", ".join(group_config["cc"])
        message["Date"] = formatdate(localtime=True)
        message["Subject"] = subject
        message.set_content(body)
        for attachment in attachment_paths:
            message.add_attachment(
                attachment.read_bytes(),
                maintype="application",
                subtype="pdf",
                filename=attachment.name,
            )
        (drafts_dir / f"{slug}.eml").write_bytes(message.as_bytes())


def plan(invoices: list[Invoice]) -> None:
    print("Planned SmartCore invoices")
    print("=" * 80)
    for invoice in invoices:
        print(
            f"#{invoice.number}: {invoice.client['company']} | {month_label(invoice.service_month)} | "
            f"{invoice.email_group} | {fmt_money(invoice.total)}"
        )
    print("=" * 80)
    print(f"Total invoices: {len(invoices)}")
    print(f"Total amount: {fmt_money(sum((invoice.total for invoice in invoices), Decimal('0.00')))}")


def generate(config: dict[str, Any], invoices: list[Invoice], transition_note: bool) -> Path:
    output_dir = invoice_output_dir(config, invoices[0].invoice_date)
    invoice_dir = output_dir / "invoices"
    html_dir = output_dir / "html"
    invoice_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    pdf_paths: dict[int, Path] = {}
    for invoice in invoices:
        pdf_path = invoice_dir / invoice_filename(invoice, "pdf")
        html_path = html_dir / invoice_filename(invoice, "html")
        draw_invoice_pdf(invoice, pdf_path)
        write_html(invoice, html_path)
        pdf_paths[invoice.number] = pdf_path
    write_email_drafts(config, invoices, output_dir, pdf_paths, transition_note=transition_note)
    write_ledger(invoices, output_dir, pdf_paths)
    print(f"Generated SmartCore billing package: {output_dir}")
    print(f"Invoices: {invoice_dir}")
    print(f"HTML previews: {html_dir}")
    print(f"Email drafts: {output_dir / 'email_drafts'}")
    print(f"Ledger: {output_dir / LEDGER_NAME}")
    return output_dir


def validate_config(config: dict[str, Any]) -> int:
    errors: list[str] = []
    logo_path = ROOT / config["company"].get("logo_path", "")
    if not logo_path.exists():
        errors.append(f"Missing logo: {logo_path}")
    for invoice in config.get("recurring_invoices", []):
        if invoice["client"] not in config["clients"]:
            errors.append(f"Missing client for recurring invoice: {invoice['key']}")
        if invoice["email_group"] not in config["email_groups"]:
            errors.append(f"Missing email group for recurring invoice: {invoice['key']}")
        if invoice_total(invoice.get("line_items", [])) <= 0:
            errors.append(f"Invoice has no positive total: {invoice['key']}")
    if errors:
        print("SmartCore billing config has issues:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SmartCore billing config OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate SmartCore invoice PDFs and email draft packages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("plan", "generate"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--invoice-date", required=True, type=parse_date, help="Invoice date, YYYY-MM-DD.")
        sub.add_argument("--service-months", required=True, nargs="+", type=parse_month, help="One or more service months, YYYY-MM.")
        sub.add_argument("--start-number", required=True, type=int, help="First invoice number to generate.")
        sub.add_argument("--transition-note", action="store_true", help="Include billing-email transition note in draft bodies.")

    subparsers.add_parser("validate")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = read_config()
    if args.command == "validate":
        return validate_config(config)

    invoices = build_invoices(
        config=config,
        invoice_date=args.invoice_date,
        service_months=args.service_months,
        start_number=args.start_number,
    )
    plan(invoices)
    if args.command == "generate":
        generate(config, invoices, transition_note=args.transition_note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
