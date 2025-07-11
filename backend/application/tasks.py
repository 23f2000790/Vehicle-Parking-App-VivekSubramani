from celery import shared_task
import time

@shared_task(ignore_results = False, name = "download_csv_report")
def csv_report():
    time.sleep(3)
    return "Started csv report"