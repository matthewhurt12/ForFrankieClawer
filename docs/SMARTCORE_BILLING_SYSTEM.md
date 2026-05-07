# SmartCore Billing System

This workflow generates monthly SmartCore Solutions invoices and email draft
packages. It does not send email automatically.

## First Command

Preview the next billing run:

```powershell
python scripts\smartcore_billing.py plan --invoice-date 2026-05-05 --service-months 2026-03 2026-04 --start-number 62
```

Generate PDFs, HTML previews, and email drafts:

```powershell
python scripts\smartcore_billing.py generate --invoice-date 2026-05-05 --service-months 2026-03 2026-04 --start-number 62
```

Generated files are written under:

```text
data/smartcore_billing/generated/YYYY-MM-DD/
```

## Current Recurring Bills

- Donaldson Garrett & Associates Inc: Vehicle Tracking
- Progressive Communications: Asset Tracking
- Progressive Properties: Building Monitoring

Edit `config/smartcore_billing.json` to change recipients, line items, rates,
company address, or service labels.

## Email Safety

The script creates draft packages only:

- `.txt` with subject, recipients, body, and attachment paths
- `.eml` with PDFs attached

Frankie may prepare drafts, but should not send invoices unless Matthew
explicitly asks for sending and the recipients/attachments are reviewed.

## Future Gmail Integration

When Matthew gives Frankie access to the SmartCore billing mailbox, add a
separate guarded send/draft command. Keep the current `generate` command
local-only so the normal monthly workflow can be checked safely.
