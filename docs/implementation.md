# Implementation Notes

## Data rule

Garmin payloads are stored in `raw_garmin_payloads` before normalization. Derived metrics and AI insights cite raw or computed records through `evidence_refs`.

## AI safety rule

Hermes agents cannot emit an insight without evidence. Medical diagnosis, treatment, medication, or emergency claims are rejected by the safety agent contract.

## Garmin fallback

The primary path is Garmin API OAuth. If API access is delayed, CSV/JSON export ingestion should write into the same raw payload table with `source = "garmin_export"` so the rest of the system remains unchanged.

