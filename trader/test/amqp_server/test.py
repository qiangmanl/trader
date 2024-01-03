
from tasks_amqp.tasks import update_task
result = update_task.delay(3,6).get()
