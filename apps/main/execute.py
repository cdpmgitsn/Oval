from apscheduler.schedulers.background import BackgroundScheduler
from .scheduler_jobs import decrease_subscription


scheduler = BackgroundScheduler()
scheduler.add_job(decrease_subscription, 'interval', seconds=5)
scheduler.start()
