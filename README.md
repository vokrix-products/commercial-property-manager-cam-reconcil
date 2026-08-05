# Commercial Property Manager CAM Reconciliation & Tenant Charge Pre-Compiler (5-50 Tenant Tier)

This backend service is the pre-compiler for the CAM (Common Area Maintenance) reconciliation workflow. It accepts raw document bytes from the poller, extracts tenant charge records, and classifies each charge against a fixed threshold of $5,000.

## Product Archetype

- **Tier:** 5-50 tenants
- **Backend:** Pure Python processor with no web framework; designed to be invoked by an external poller
- **Extraction:** DeepSeek LLM (deepseek-chat) via the OpenAI SDK
- **Input formats:** PDF, Excel (.xlsx), CSV, plain text
- **Threshold:** 5000.0 - charges above this are `above_threshold:critical`, otherwise `within_threshold:good`

## What the Poller Expects to Send

The poller calls `process_file(file_bytes)` from `processor.py` with the raw bytes of an uploaded document. The function returns a list of records, each shaped as:

```json
{
  "title": "Tenant Name",
  "status": "above_threshold:critical | within_threshold:good",
  "details": {
    "charge_amount": 12000.0,
    "property": "Sunset Towers"
  },
  "due_date": "2025-05-15"
}
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set your DeepSeek API key:
   ```
   export DEEPSEEK_API_KEY=your_key_here
   ```

## Run

### Demo
```
python3 run_demo.py
```

### Tests
```
python3 run_tests.py
```
Dashboard: https://commercial-property-manager-cam-reconcil.vokrix.co
Vercel: commercial-property-manager-cam-reconcil
Railway: 36234174-1035-4c9d-bbbc-9f7034837073
Railway: commercial-property-manager-cam-reconcil
