import threading
import pyttsx3


# 以函数方式快速调用朗读器

MUTEX = threading.Lock()

# 获取系统已安装的所有朗读者的信息列表
def getReadersInfo() :
    try :
        return pyttsx3.init().getProperty('voices')
    except Exception :
        return []

# voice_idx 指定使用本地的第几号朗读者
# speed 朗读速度，词/分钟
# volume 朗读音量，0.0~1.0
def readAloud(text, voice_idx=0, speed=150, volume=1.0) :
    # 同时只能有一个线程在朗读
    if not MUTEX.acquire(blocking=False) :
        return
    try :
        engine = pyttsx3.init()
        engine.setProperty("voice", engine.getProperty('voices')[voice_idx].id)
        engine.setProperty('rate', speed)
        engine.setProperty('volume', volume)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except RuntimeError as err :
        pass
    finally :
        MUTEX.release()


# 以类的方式调用朗读器
# TODO 未测试
class LoudReader :
    def __init__(self) :
        self.mutex = threading.Lock()
        self.engine = pyttsx3.init()
        self.started = False

    def getReadersInfo(self) :
        return self.engine.getProperty('voices')

    def start(self) :
        if not self.started :
            self.engine.startLoop(False)
            self.started = True

    def readAloud(self, text, voice_idx=0, speed=150, volume=1.0) :
        if self.started :
            if not self.mutex.acquire(blocking=False) :
                return
            try:
                self.engine.setProperty("voice", engine.getProperty('voices')[voice_idx].id)
                self.engine.setProperty('rate', speed)
                self.engine.setProperty('volume', volume)
                self.engine.say(text)
                self.engine.iterate()
            except RuntimeError as err :
                print(err)
            finally:
                self.mutex.release()

    def stop(self) :
        if self.started :
            self.engine.endLoop()
            self.started = False
