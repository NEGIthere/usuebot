import db_manager
import lessons

#from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

#sched = BlockingScheduler()
sched = BackgroundScheduler()
'''
@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')
    lessons.updateAllTimeTable()
'''

db_manager.init()

job = scheduler.add_job(lessons.updateAllTimeTable, 'interval', minutes=1) # lessons.updateAllTimeTable

sched.start()