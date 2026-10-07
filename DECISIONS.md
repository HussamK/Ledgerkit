## 001. Store money as integer cents
*2026-10-05*

**Decision.**

All amounts are stored as BigIntegerField in integer cents.

**Alternatives.** 

FloatField or DecimalField storing dollars.

**Why.** 

Floats can't represent most decimal fractions exactly (0.1 + 0.2 != 0.3), so repeated arithmetic drifts, and the ledger's core rule, that every transaction sums to exactly zero, becomes unreliable. Decimals are exact, but integer cents are simpler, faster, and make the sum-to-zero check a plain integer comparison.

**Cost.** 

Single-currency assumption: cents only work for currencies with two decimal places. Callers must convert dollars to cents themselves, and an off-by-100 bug at the API boundary is easy to make. The field names (amount_cents) exist to make that hard to miss.

## 002. Balance enforcement in the service layer
*2026-10-05*
**Decision.**

record_transaction checks the legs sum to zero before writing anything

**Alternatives.** 

A Postgres constraint

**Why.** 

Quick to do first, easy to test, rejects input before anything is written and gives readable error messages

**Cost.** 

Single-currency assumption: cents only work for currencies with two decimal places. Callers must convert dollars to cents themselves, made easier to remember by requiring amount_cents

## 003. Idempotency Keys in a separate table
*2026-10-05*
**Decision.**

The Idempotency-Key header is required on POST /obligations/, and the record is unique on (key, endpoint)

**Alternatives.** 

A idempotency_key column directly on Obligation table

**Why.** 

Can be reused for any endpoint, replays the original response exactly and have a records to look up if necessary
Same key sent to two different endpoints describes two different operations, so uniqueness is on (key, endpoint), not the key alone

**Cost.** 

Record, obligation and ledger entries must commit in one transaction, with a save point around the record insert, stored records also don't expire

## 004. System accounts seeded by a data migration
*2026-10-05*

**Decision.**

Platform:Cash and External:Provider are created by a migration

**Alternatives.** 

Created with a script or loaddata

**Why.**

App doesn't work without them already set and want it to be very easy to pull down and run, python manage.py migrate will handle it

**Cost.** 

Always exists in every test database