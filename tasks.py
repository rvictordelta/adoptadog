from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import adoptadog

# run the task at the start of the scheduler
adoptadog.dog_scrape()


def scrape_go():
    print(f"---beginning scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    adoptadog.dog_scrape()
    print(f"---finished  scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


scheduler = BlockingScheduler()
scheduler.add_job(scrape_go, 'interval', hours=2)
scheduler.start()
