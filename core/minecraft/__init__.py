import logging
from mcpi import vec3
from mcpi.minecraft import Minecraft as mf
from core.minecraft.jython import Jython
import schedule


class Minecraft:
    def __init__(self):
        self.__mcpi = mf.create()
        self.jython = Jython()
        # 每秒定时获取玩家发送的消息
        schedule.every().seconds.do(self.__process_msg)
        self.__handle = None
        # 位置记录
        self.pose = {}

    # 发送消息
    def post_msg(self, content: str):
        logging.info("[minecraft] post message: {}".format(content))
        self.__mcpi.postToChat(content)

    def register_handle(self, handle):
        self.__handle = handle

    # 获取玩家的位置
    def get_position(self, name: str) -> vec3:
        return self.__mcpi.entity.getPos(self.__get_entity_id(name))

    # 设置玩家的位置
    def set_position(self, name: str, pos_name: str):
        self.__mcpi.entity.setPos(self.__get_entity_id(name), self.pose[pos_name])

    def __get_entity_id(self, name: str) -> int:
        return self.__mcpi.getPlayerEntityId(name)

    def __handle_message(self, name: str, msg: str):
        if self.__handle is not None:
            self.__handle(name, msg)

    # 定时处理消息
    def __process_msg(self):
        events = self.__mcpi.events.pollChatPosts()
        if len(events) > 0:
            for event in events:
                name = self.__mcpi.entity.getName(event.entityId)
                logging.info("[minecraft] {}: {}".format(name, event.message))
                self.__handle_message(name, event.message)

    def close(self):
        self.jython.close()
