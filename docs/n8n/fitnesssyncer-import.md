# FitnessSyncer + n8n Import Flow

## Goal

Use FitnessSyncer as the Garmin data source and n8n as the automation layer. HealthOS receives CSV files and stores the original rows before normalizing them into health tables.

## Recommended VPS Folder

FitnessSyncer exports should land here on the VPS:

```text
data/imports
```

Docker Compose mounts that folder into the API container at the same relative path:

```text
/app/data/imports
```

## Option A: n8n posts the CSV directly

Use an n8n HTTP Request node:

- Method: `POST`
- URL: `https://YOUR_HEALTHOS_API/imports/fitnesssyncer`
- Authentication: Bearer token from `POST /auth/login`
- Body Content Type: multipart form-data
- File field name: `file`

## Option B: n8n saves the CSV locally, then triggers import

1. Save the FitnessSyncer CSV into `data/imports` on the VPS.
2. Call:

```http
POST /imports/fitnesssyncer/local
Content-Type: application/json
Authorization: Bearer TOKEN

{
  "path": "fitnesssyncer_mock.csv"
}
```

The API only imports files inside `IMPORT_STORAGE_DIR`.

## Mock CSV

Use this fixture to test the workflow before real Garmin data is available:

```text
samples/fitnesssyncer_mock.csv
```

## Supported MVP Record Types

- `sleep`
- `hrv`
- `stress`
- `activity`
- `steps`
- `resting_hr`
- `spo2`

## MVP Columns

Required:

- `record_type`
- `start_time`

Recommended:

- `end_time`
- `value`
- `unit`
- `source_id`
- `score`
- `interruptions`
- `baseline`
- `deviation_pct`
- `sport_type`
- `distance_meters`
- `training_effect`
- `load_score`
- `notes`

## Operational Notes

- HealthOS stores every row as a raw payload before normalization.
- Parser errors are saved on the import batch instead of aborting the entire file.
- Unknown `record_type` rows are skipped but still stored as raw payloads.
- The exact FitnessSyncer export columns can be mapped later once we have a real export file.
