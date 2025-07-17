def processing_log_schema(log) -> dict:
    return {
        "id": str(log["_id"]),
        "invoice_filename": log["invoice_filename"],
        "image_url": log["image_url"],
        "status": log["status"],
        "error_message": log.get("error_message"),
        "processing_run_id": log["processing_run_id"],
        "created_at": log["created_at"]
    }


def processing_logs_schema(logs) -> list:
    return [processing_log_schema(log) for log in logs]
