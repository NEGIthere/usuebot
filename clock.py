import db_manager
import lessons

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')
    lessons.updateAllTimeTable()

db_manager.init()
sched.start()