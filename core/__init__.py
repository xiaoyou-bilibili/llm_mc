from core.minecraft import Minecraft
import logging

from core.base import Base
from core.database import ChromadbDb, TextType
from kani.engines.openai import OpenAIEngine
from core.llm import MinecraftAi
from core.minecraft import Minecraft
import asyncio


class MinecraftAssistant:
    def __init__(self):
        self.__mc = Minecraft()
        self.__mc.register_handle(self.__handle_mc_message)
        self.__base = Base()
        self.__db = ChromadbDb()
        self.__engine = OpenAIEngine(self.__base.openapi_key, model="gpt-3.5-turbo", api_base=self.__base.openapi_base)
        self.__loop = asyncio.new_event_loop()
        self.__mc.post_msg("§6§l 我的世界大语言助手 by:小游")
        self.__mc.post_msg("§3 [ai]: 你好，请问有啥需要？")

    def __handle_mc_message(self, name: str, message: str):
        answer = self.ask(name, message)
        self.__mc.post_msg("§3 [ai]: {}".format(answer))

    # 异步询问问题
    async def ask_sync(self, name: str, question: str) -> str:
        prompt = "你是一个游戏助手，下面会给出一些背景信息，你需要根据背景信息来执行操作或者解答玩家的问题，" \
                 "请不要回答和背景信息无关的内容，如果玩家需要生成或给予物品，给一个最相似的即可，背景信息如下：\n玩家名字为：{}\n".format(name)
        pose_list = []
        for pose in self.__mc.pose:
            pose_list.append(pose)
        if len(pose_list) > 0:
            prompt += "位置列表：{}\n".format(",".join(pose_list))
        # 查询背景知识
        data = self.__db.query_content(question, 20)
        entity, material, brewing, command, enchantment = [], [], [], [], []
        for i in range(len(data['ids'][0])):
            text_type = data['metadatas'][0][i]['type']
            document = data['documents'][0][i]
            if text_type == TextType.Entity.value:
                entity.append(document)
            elif text_type == TextType.Material.value:
                material.append(document)
            elif text_type == TextType.Brewing.value:
                brewing.append(document)
            elif text_type == TextType.Command.value:
                command.append(document)
            elif text_type == TextType.Enchantment.value:
                enchantment.append(document)
        if len(entity) > 0:
            prompt += "实体id：{}\n".format(",".join(entity))
        if len(material) > 0:
            prompt += "物品id：{}\n".format(",".join(material))
        if len(enchantment) > 0:
            prompt += "附魔类型：{}\n".format(",".join(enchantment))
        if len(brewing) > 0:
            prompt += "药水说明：{}\n".format(",".join(brewing))
        if len(command) > 0:
            prompt += "指令说明(需要明确的问指令才能回答)：{}\n".format(",".join(command))
        logging.info("[game-ai] prompt is {}".format(prompt))
        mc_ai = MinecraftAi(self.__engine, self.__mc, name, prompt=prompt)
        answers = []
        async for msg in mc_ai.full_round(question):
            logging.info("[game-ai] answer {}".format(msg))
            if msg.content is not None:
                answers.append(msg.content)
        return "\n".join(answers)

    # 同步执行
    def ask(self, name: str, question: str) -> str:
        return self.__loop.run_until_complete(self.ask_sync(name, question))

    def close(self):
        self.__loop.close()
