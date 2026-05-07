# SmartCore Billing Data

Generated invoice PDFs, HTML previews, and email draft packages go under:

```text
data/smartcore_billing/generated/
```

That generated folder is ignored by Git. Keep durable billing setup in:

- `config/smartcore_billing.json`
- `scripts/smartcore_billing.py`
- `skills/smartcore-billing/SKILL.md`

Do not commit sent-mail exports, private payment records, tokens, or raw Gmail
data.
