# Ledgerkit

A double-entry payout ledger. Records obligations, batches payouts to an
external provider, and reconciles against what the provider actually processed.

Built as a study in correctness under failure: every movement of money is
recorded as balanced, immutable entries, and money is only ever recorded as
moved once the provider confirms it.

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
git clone https://github.com/yourname/ledgerkit.git
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

In progress. Currently: project setup and ledger schema.