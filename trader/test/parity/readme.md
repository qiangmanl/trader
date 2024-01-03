#### run
```bash
# tasks.py 是入口文件
celery -A tasks worker --loglevel=info
#如果需要定时任务
celery -A tasks beat
#
```

```python

import pandas as pd
import numpy as np

np.random.seed(42)
index = pd.date_range(start='2014-01-01', end='2024-01-01', freq='30T')
close = np.random.choice([0, 1], size=len(index), p=[0.5, 0.5])
df = pd.DataFrame(data={'close': close}, index=index)
df.index.name = "datetime"
df.to_csv('~/.trader/row/parity2.SZ.csv', index=True)



self.SZparity2.history[self.SZparity2.history.index.date == self.yesterday]

```