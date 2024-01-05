import sys
from loguru import logger

class Logger:
    def __init__(self, 
        **kwargs
    ):
        logger.remove()
        if kwargs == {}:
            level = "INFO"
            logger.add(sys.stderr, level=level)
        else:
            level = kwargs.setdefault("level","INFO").upper()
            path = kwargs.get("path",None)

            if path:
                rotation = kwargs.setdefault("rotation","500M")
                encoding = kwargs.setdefault("encoding","utf-8")
                enqueue = kwargs.setdefault("enqueue",True)
                compression = kwargs.setdefault("compression","zip")
                retention = kwargs.setdefault("retention","10 days")
                logger.add(
                    path,
                    level=level, 
                    rotation=rotation, 
                    encoding=encoding, 
                    enqueue=enqueue,
                    compression=compression, 
                    retention=retention
                )
            else:
                logger.add(sys.stderr, level=level)

        self.debug = logger.debug
        self.info = logger.info
        self.warning = logger.warning
        self.error = logger.error
        self.exception = logger.exception
        if level == "DEBUG":
            logger.debug(f'logger start {level} level mode')
        # logger.info(f'logger start {level} level mode')
        
    def prompt(self,courier="error"):
        """
            Usage:
                @logger.prompt("error")
                def test(): 
                    return 1/0

                if not test():
                    exit()
                print("test:yes")
                #Out:
                    2023-12-02 11:14:29,411-ERROR-division by zero
        """

        def decorator(func):   
            def wrapper(*args, **kw):
                try: 
                    result = func(*args, **kw) 
                except Exception as e:
                    match courier:
                        case "error":
                            self.error(e) 
                        case "warning":
                            self.warning(e)
                        case "exception":
                            self.exception(e)
                        case _:
                            self.exception(f'{courier} Not an available courier!') 
                    result = None
                return result
            return wrapper 
        return decorator

    def aprompt(self, courier="error"):   
        """
        Usage:
            import asyncio 
            @adoubt("exception")
            async def get():
                await asyncio.sleep(0)
                1/0
                return 1

            async def main():
                x = await get()
                print(x)
            asyncio.get_event_loop().run_until_complete(main())
            #2023-12-05 21:42:38.291 | ERROR    | __main__:wrapper:87 - division by zero
        Return 
            None
        """
        def decorator(func):     
            async def wrapper(*args, **kw):
                try: 
                    result = await func(*args, **kw) 
                except Exception as e: 
                    match courier:
                        case "error":
                            self.error(e) 
                        case "warning":
                            self.warning(e)
                        case "exception":
                            self.exception(e)
                        case _:
                            self.exception(f'{courier} Not an available courier!')                 
                    result = None
                return result
            return wrapper 
        return decorator







# def adoubt(courier="error",prompt="",**kw):   
#     """
#     Usage:
#         import asyncio 
#         @adoubt("exception")
#         async def get():
#             await asyncio.sleep(0)
#             1/0
#             return 1

#         async def main():
#             x = await get()
#             print(x)
#         asyncio.get_event_loop().run_until_complete(main())
#         #2023-12-05 21:42:38.291 | ERROR    | __main__:wrapper:87 - division by zero
#     Return 
#         None
#     """
#     try:
#         assert courier in loggers,"%s Not an available courier!"%courier
#         is_error = False
#     except AssertionError as e:
#         loggers["error"](e) #+ 
#         is_error = True
#     def decorator(func):     
#         async def wrapper(*args, **kw):
#             try: 
#                 if is_error:
#                     return None
#                 else:
#                     result = await func(*args, **kw) 
#             except Exception as e: 
#                 if prompt:
#                     loggers[courier](prompt) 
#                 else:
#                     loggers[courier](e)                    
#                 result = None
#             return result
#         return wrapper 
#     return decorator





