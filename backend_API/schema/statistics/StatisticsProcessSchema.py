def statistic_process_schema(statistic_process) -> dict:
    return {
        "id": str(statistic_process["_id"]),
        "process_date": statistic_process["process_date"],
        "total_files": statistic_process["total_files"],
        "successful": statistic_process["successful"],
        "errors": statistic_process["errors"],
        "success_rate": statistic_process["success_rate"],
        "created_at": statistic_process.get("created_at"),
        "updated_at": statistic_process.get("updated_at")
    }

def statistics_process_schema(statistics_process) -> list:
    return [statistic_process_schema(sp) for sp in statistics_process]
