import db_manager
import lessons
import logging
#from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#scheduler = BlockingScheduler()
scheduler = BackgroundScheduler()
'''
@scheduler.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')
    lessons.updateAllTimeTable()
'''

db_manager.init()

def doUpdate():
	logger.info("Updating")
	lessons.updateAllTimeTable()
	return
job = scheduler.add_job(doUpdate, 'interval', minutes=1) # lessons.updateAllTimeTable

scheduler.start()