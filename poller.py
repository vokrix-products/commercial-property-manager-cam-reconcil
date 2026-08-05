import json
import os
import time
from datetime import datetime, timezone

import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]

HEADERS = {
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "apikey": SUPABASE_SERVICE_KEY,
    "Content-Type": "application/json",
}

def download_file(bucket, file_path):
    if file_path.startswith(bucket + "/"):
        file_path = file_path[len(bucket) + 1:]
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY})
    resp.raise_for_status()
    return resp.content

def insert_notification(product_id, customer_id, title, body, ntype):
    try:
        payload = {
            "product_id": product_id,
            "customer_id": customer_id,
            "title": title,
            "body": body,
            "type": ntype,
            "read": False,
        }
        requests.post(
            f"{SUPABASE_URL}/rest/v1/notifications",
            headers=HEADERS,
            json=payload,
        )
    except Exception:
        pass

def process_job(job):
    job_id = job["id"]
    try:
        file_bytes = download_file("uploads", job["input_file_path"])
        import processor
        records = processor.process_file(file_bytes)

        source_file_path = job.get("input_file_path")
        customer_id = job.get("customer_id")
        if not customer_id:
            raise ValueError("job missing customer_id")

        if records:
            rec_payload = [
                {
                    "product_id": PRODUCT_ID,
                    "customer_id": customer_id,
                    "title": record["title"],
                    "status": record["status"],
                    "details": record["details"],
                    "source_file_path": source_file_path,
                    "due_date": record.get("due_date"),
                }
                for record in records
            ]
            resp = requests.post(f"{SUPABASE_URL}/rest/v1/records", headers=HEADERS, json=rec_payload)
            resp.raise_for_status()

        result = {"records": records, "record_count": len(records)}
        result_bytes = json.dumps(result, default=str).encode("utf-8")
        output_path = f"results/{job_id}/{datetime.now(timezone.utc).isoformat()}.json"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/results/{output_path}"
        resp = requests.post(
            upload_url,
            headers={"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", "apikey": SUPABASE_SERVICE_KEY, "Content-Type": "application/json"},
            data=result_bytes,
        )
        resp.raise_for_status()

        summary = f"Processed {len(records)} record(s)."
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}",
            headers=HEADERS,
            json={
                "status": "completed",
                "output_file_path": output_path,
                "result_summary": summary,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        ).raise_for_status()
        insert_notification(PRODUCT_ID, customer_id, "Processing complete", "Your upload has been processed successfully.", "success")
    except Exception as e:
        customer_id = job.get("customer_id")
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}",
            headers=HEADERS,
            json={
                "status": "failed",
                "result_summary": str(e),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        ).raise_for_status()
        insert_notification(PRODUCT_ID, customer_id, "Processing failed", "There was an error processing your upload.", "error")

def main():
    while True:
        try:
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/jobs",
                headers=HEADERS,
                params={
                    "status": "eq.pending",
                    "job_type": "eq.process_upload",
                    "product_id": f"eq.{PRODUCT_ID}",
                    "order": "created_at.asc",
                },
            )
            resp.raise_for_status()
            jobs = resp.json()
            for job in jobs:
                process_job(job)
        except Exception:
            pass
        time.sleep(60)

if __name__ == "__main__":
    main()
