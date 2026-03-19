import os
from app.core.config import settings

def pdf_dir(user_id: str, crawl_job_id: str) -> str:
    return os.path.join(settings.storage_root, "pdfs", user_id, crawl_job_id)

def wordcloud_dir(user_id: str) -> str:
    return os.path.join(settings.storage_root, "wordclouds", user_id)