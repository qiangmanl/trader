from celery import Celery
from trader import config
"""
    不要在此页执行可能阻塞的指令， 比如直接调用task函数
"""
broker='amqp://guest@localhost//'
backend='rpc://'
if hasattr(config,"amqp_celery"):
    broker  = config.amqp_celery.get("broker",broker)
    backend = config.amqp_celery.get("backend" ,backend)

app = Celery('trader_tasks' , broker=broker,backend=backend)
app.conf.update(
    include=['trader.amqp_server.tasks'],
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


# import pdb

# pdb.set_trace()



