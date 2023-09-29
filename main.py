# -*- coding: utf-8 -*-
import time
import schedule
from core import MinecraftAssistant
import logging


# 配置日志记录
logging.basicConfig(level=logging.INFO)
if __name__ == '__main__':
    assistant = MinecraftAssistant()
    try:
        while True:
            schedule.run_pending()
            time.sleep(0.1)
    except KeyboardInterrupt:
        assistant.close()
