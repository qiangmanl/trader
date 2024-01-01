import time 
import asyncio
import signal
import inspect
from trader import logger, node_id



__all__ = ("looper","SingleTask")


class HeartBeat:
    """ 心跳
    """

    def __init__(self,heartname, interval, print_interval)->None:
        self.heartname = heartname
        self._count = 0  # 心跳次数
        self._print_in_count = 0
        interval = round(interval,7)
        if not interval:
            interval = 1/10 ** 7
        self._interval = interval  # 服务心跳执行时间间隔(秒)
        print_interval = int(print_interval)
        if print_interval < 0:
            print_interval = 1
        self._print_interval = print_interval
        self._tasks = None


    @property
    def count(self)->int:
        return self._count

    def ticker(self):
        """ 
        """
        self._count += 1
        if (time.time() % self._print_interval) == 0:
            #
            if self._print_in_count < self._count:
                msg = f'MSG:::HeartBeat.ticker:::do heartbeat:{self.name}, count:{int(self._count / 200)}'
                logger.info(msg)
                self._print_in_count = self._count 
        # 下一次心跳间隔
        asyncio.get_event_loop().call_later(self._interval, self.ticker)

        # 执行任务回调
        if self.heartname:
            func = self._task["func"]
            args = self._task["args"]
            kwargs = self._task["kwargs"]
            kwargs["name"] = self.heartname
        
            asyncio.get_event_loop().create_task(func(*args, **kwargs))

    def register(self, func, *args, **kwargs)->str:
        """ 注册一个任务，在每次心跳的时候执行调用
        @param func 心跳的时候执行的函数,时间间隔self._interval
        """
        task = {
            "func": func,
            "args": args,
            "kwargs": kwargs
        }
        self._task = task
        return self.heartname

    def unregister(self):
        del self.task
        del self.heartname



class Looper:
    """ Asynchronous driven quantitative trading framework.
    """

    def __init__(self, project):
        """
            heartbeats  is heartname to heartbeat_object
            
        """
        self.heartbeats = dict()
        self.loop = None
        self.project = project
        logger.info(f'MSG:::Looper:::[project:{self.project}] initiating...')
        self._get_event_loop()
        self.__ticked = None

    def start(self):
        """Start the event loop."""
        self._beat()
        def keyboard_interrupt(s, f):
            print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(s))
            self.loop.stop()
        signal.signal(signal.SIGINT, keyboard_interrupt)
        logger.info(f'MSG:::Looper:::Start in \"[project:{self.project}]\" io loop...')
        self.loop.run_forever()

    def stop(self):
        """Stop the event loop."""
        logger.info(f'MSG:::Looper:::Stop in \"[project:{self.project}]\" io loop...')
        self.loop.stop()

    def _get_event_loop(self):
        """ Get a main io loop. """
        if not self.loop:
            self.loop = asyncio.get_event_loop()
            #self.loop.set_debug(True)
        return self.loop

    def _beat(self):
        """Start server heartbeat."""
        for _, heartbeat in self.heartbeats.items():
            self.loop.call_later(0.5, heartbeat.ticker)
        logger.info("all heartbeat ticked")
        self.__ticked = True



    def register(self,  func, *args, **kwargs)->str:
  
        """ Register a loop run.

        Args:
            func: Asynchronous callback function.
            interval: execute interval time(seconds), default is 1s.

        Returns:
            task_id: Task id.
        """
        heartname = kwargs.pop("heartname",None)
        if not heartname:
            logger.error("heartbeat need a name what you are aware of")
            return 
        interval = kwargs.pop("interval",0.1)
        print_interval = kwargs.pop("print_interval",60)
        heartbeat = HeartBeat(heartname=heartname, interval=interval, print_interval=print_interval)
        if not self.__ticked:
            self.heartbeats[heartname] = heartbeat
            heartbeat.register(func, *args, **kwargs)
        return heartname

    def unregister(self,heartname)->None:
        """ Unregister a loop run task.
        Args:
            task_id: Task id.
        """
        self.heartbeats[heartname].unregister()
        self.heartbeats[heartname].pop()
    

class SingleTask:
    """ Single run task.
    """

    @classmethod
    def run(cls, func, *args, **kwargs):
        """ Create a coroutine and execute immediately.

        Args:
            func: Asynchronous callback function.
        """
        asyncio.get_event_loop().create_task(func(*args, **kwargs))

    @classmethod
    def call_later(cls, func, delay=0, *args, **kwargs):
        """ Create a coroutine and delay execute, delay time is seconds, default delay time is 0s.

        Args:
            func: Asynchronous callback function.
            delay: Delay time is seconds, default delay time is 0, you can assign a float e.g. 0.5, 2.3, 5.1 ...
        """
        # import pdb 
        # pdb.set_trace()
        if not inspect.iscoroutinefunction(func):
            asyncio.get_event_loop().call_later(delay, func, *args)
        else:
            def foo(f, *args, **kwargs):
                asyncio.get_event_loop().create_task(f(*args, **kwargs))
            asyncio.get_event_loop().call_later(delay, foo, func, *args)


looper = Looper(project=node_id)