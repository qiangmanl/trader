#### run
```bash
# tasks.py 是入口文件
celery -A tasks worker --loglevel=info
#如果需要定时任务
celery -A tasks beat
#
```

```python

import asyncio 
import time

from trader.strategy import HistoricalStrategy
from trader.main import run

class MyStrategy(HistoricalStrategy):
    index_name="trade_time"
    useful_column=['open', 'high', 'low', 'close', 'vol']
    async def start(self):
        print(self.flows_window)
        print(time.time())
        self.sell("test",1)
    
if __name__ == "__main__":
    run(MyStrategy) 

```