from celery import Celery
broker='amqp://guest@localhost//'
backend='rpc://'    
app = Celery('trader_tasks' , broker=broker,backend=backend)
app.conf.update(
    include=['tasks_amqp.tasks'],
    ACKS_LATE=True,  # 允许重试
    ACCEPT_CONTENT=['pickle', 'json'],
    TASK_SERIALIZER='json',
    RESULT_SERIALIZER='json',
    # 设置并发worker数量
    WORKER_CONCURRENCY=4, 
    # 每个worker最多执行500个任务被销毁，可以防止内存泄漏
    MAX_TASKS_PER_CHILD=500, 
    broker_heartbeat=0,  # 心跳
    TASK_TIME_LIMIT=12 * 30,  # 超时时间
    broker_connection_retry_on_startup=True,
    CELERY_ENABLE_UTC=True,
    TIMEZONE='Asia/Shanghai'
)


trader_tasks = dict()

@app.task
def update_task(symbol,task):
    trader_tasks.update({symbol:task})
    return True
