import logging

from kani import Kani, ai_function, AIParam
from kani.engines.openai import OpenAIEngine
from kani.models import ChatMessage
from typing import Annotated
from core.minecraft import Minecraft


class MinecraftAi(Kani):
    def __init__(self, engine: OpenAIEngine, mc: Minecraft, name: str, prompt: str = '',
                 history: list[ChatMessage] = []):
        super().__init__(engine, system_prompt=prompt, chat_history=history)
        self.__mc = mc
        self.__name = name

    @ai_function(desc="可以修改游戏时间为任意时刻")
    def set_time(self, time: Annotated[int, AIParam(
        desc="时间信息， 黎明: 0；早上：1000；上午：3000；中午：6000；下午：7000；黄昏：11616；晚上：13800；午夜：18000")]):
        self.__mc.jython.time(time)
        return True

    @ai_function(desc="在玩家面前落下一道闪电（打雷）")
    def bolt(self):
        self.__mc.jython.bolt(self.__name)
        return True

    @ai_function(desc="在玩家面前触发一个爆炸")
    def explosion(self):
        self.__mc.jython.explosion(self.__name)
        return True

    @ai_function(desc="在玩家面前生成一个物体，可能问法：生成xxx")
    def swap(self, entity_id: Annotated[int, AIParam(desc="实体id")]):
        self.__mc.jython.swap(self.__name, entity_id)
        return True

    @ai_function(desc="给予玩家一个或多个物品，只要问题里有给字即可")
    def give(self, material_id: Annotated[int, AIParam(desc="物品id")], num: Annotated[int, AIParam(desc="物品数量")]):
        self.__mc.jython.give(self.__name, material_id, num)
        return True

    @ai_function(desc="给予玩家个附魔装备，eg：给我一把截肢杀手为10级的钻石剑")
    def give_enchantment(self, enchantment_type: Annotated[int, AIParam(desc="附魔类型")], material_id: Annotated[int, AIParam(desc="物品id")],
                         level: Annotated[int, AIParam(desc="等级：1-10")]):
        self.__mc.jython.enchantment(self.__name, material_id, enchantment_type, level)
        return True

    @ai_function(desc="记录玩家当前的位置并做标记，可能问法：登记当前位置为，把这个地方设置为")
    def get_position(self, name: Annotated[str, AIParam(desc="位置的名字")]):
        pos = self.__mc.get_position(self.__name)
        self.__mc.pose[name] = pos
        logging.info("[ai-function] set pose {}, name {}".format(pos, name))
        return pos

    @ai_function(desc="传送玩家到某个地方，需要从位置列表里去找位置，可能问法：去xx，传送到xx")
    def set_position(self, name: Annotated[str, AIParam(desc="位置名字")]):
        self.__mc.set_position(self.__name, name)
        return True
