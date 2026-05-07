# SmartCore Billing Skill

Use this skill when Matthew asks about SmartCore invoices, monthly billing,
billing PDFs, invoice emails, billing@smartcorefleet.com, quote/proposal
generation, or sending recurring SmartCore service bills.

## Safety Defaults

- Default to local generation only.
- Do not send email unless Matthew explicitly asks for sending and confirms
  recipients and attachments.
- Do not print tokens, mailbox credentials, Gmail raw data, or private payment
  records.
- Generated customer-facing emails are drafts for Matthew to review.

## First Commands

Validate the billing config:

```powershell
python scripts\smartcore_billing.py validate
```

Preview a billing package:

```powershell
python scripts\smartcore_billing.py plan --invoice-date 2026-05-05 --service-months 2026-03 2026-04 --start-number 62
```

Generate PDFs, HTML previews, and email drafts:

```powershell
python scripts\smartcore_billing.py generate --invoice-date 2026-05-05 --service-months 2026-03 2026-04 --start-number 62
```

Add `--transition-note` when Matthew wants the billing-address change note in
the draft email body.

## Output

Generated files go under:

```text
data/smartcore_billing/generated/YYYY-MM-DD/
```

Open these after generation:

- `invoice_ledger.csv`
- `invoices/*.pdf`
- `html/*.html`
- `email_drafts/*.txt`
- `email_drafts/*.eml`

## Config

Billing setup lives in:

```text
config/smartcore_billing.json
```

It controls:

- SmartCore company address and billing email
- Logo path
- Customers and billing contacts
- Recurring services, quantities, and prices
- Email subject templates and recipients

## Current Recurring Services

- Donaldson Garrett & Associates Inc: Vehicle Tracking
- Progressive Communications: Asset Tracking
- Progressive Properties: Building Monitoring

## Email Rule

For now, generate `.txt` and `.eml` draft packages only. A future Gmail draft
integration may be added after Matthew gives access to the SmartCore billing
mailbox. Keep that as a separate guarded command.
