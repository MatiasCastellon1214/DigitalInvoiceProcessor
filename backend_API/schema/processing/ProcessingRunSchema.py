def processing_run_schema(run) -> dict:
    return {
        "id": str(run["_id"]),
        "name": run.get("name"),
        "folder_path": run["folder_path"],
        "total_files": run["total_files"],
        "successful": run["successful"],
        "errors": run["errors"],
        "success_rate": run["success_rate"],
        "invoices": [str(inv) for inv in run.get("invoices") or []],
        "excel_report_path": run.get("excel_report_path"),
        "started_at": run["started_at"],
        "ended_at": run["ended_at"],
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at")
    }

def processing_runs_schema(runs) -> list:
    return [processing_run_schema(run) for run in runs]
