from apscheduler.schedulers.blocking import BlockingScheduler

def timed_job():
    print('This job is run every three minutes.')

if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(timed_job, 'interval', id='timed_job', seconds=5)