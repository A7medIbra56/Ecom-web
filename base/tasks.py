from celery import shared_task
import logging

# Retry configuration example:
@shared_task(bind=True, max_retries=3)
def sample_task(self):
    try:
        with open("celery_test_log.txt", "a") as f:
            f.write("Redis Running\n")
        return "Redis Running"
    except Exception as e:
        # Log exception to avoid task failure without insight
        self.retry(exc=e)   
        logging.error(f"Task failed: {e}")
        raise ValueError("Naive datetime is not allowed")
