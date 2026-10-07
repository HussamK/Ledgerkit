# Ledgerkit

A double-entry payout ledger. Records obligations, batches payouts, and reconciles against what the provider actually processed.

Built as a study in correctness under failure: every movement of money is recorded as balanced, immutable entries, and money is only ever recorded as moved once the provider confirms it.

## Why double-entry

A mutable `balance` column can't answer why a balance is what it is, can't be
audited, and can't be reconstructed after a bad write. This service stores
immutable entries instead a balance is the sum of an account's entries, never
a stored value. Every transaction's entries sum to zero, so money is never
created or destroyed, only moved.

## Stack

Python · Django REST Framework · PostgreSQL · pytest · Docker

## Running locally

Requires Python 3.11+ and Docker.

```bash
git clone https://github.com/HussamK/ledgerkit.git
cd ledgerkit

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # fill in SECRET_KEY
docker compose up -d        # starts Postgres
python manage.py migrate
python manage.py runserver
```

## Status

In progress. Design decisions are recorded in [DECISIONS.md](DECISIONS.md).

**Working**
- [x] Double-entry ledger: accounts, transactions, and immutable entries; every transaction must sum to zero
- [x] Recipients and obligations, created through a service layer that writes ledger entries atomically
- [x] `POST /api/recipients/` and `POST /api/obligations/`
- [x] Idempotency keys on `POST /api/obligations/`: retries replay the original response; a reused key with a different body is rejected
- [x] System accounts seeded by data migration, so a fresh `migrate` is ready to use
- [x] pytest suite covering the ledger invariant, rollback on failure, and the API

**In progress**
- [ ] Read endpoints: obligation lookup and recipient balance (computed from entries, never stored)

**Next**
- [ ] CI: ruff and pytest against Postgres on every push
- [ ] Database-level enforcement of the sum-to-zero rule (constraint trigger)
- [ ] Payout batching: spec first, then implementation
- [ ] Simulated payment provider with retries, timeouts, and a dead-letter table
- [ ] Deployment to AWS