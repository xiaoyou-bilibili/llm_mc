import logging
from core.minecraft.enum import entity_enum, material_enum, enchantment_enum
from websockets.sync.client import connect
import schedule


class Jython:
    def __init__(self):
        self.__ws = connect("ws://127.0.0.1:44445")
        # 每秒定时获取控制器输出
        schedule.every().seconds.do(self._process_recv)
        self.__ws.send('from mcapi import *')
        # 引入实体
        self.__ws.send('from org.bukkit.entity import EntityType, Player')
        # 引入方块
        self.__ws.send('from org.bukkit import Material, GameMode')
        self.__ws.send('from org.bukkit.inventory import ItemStack')
        self.__ws.send('from org.bukkit.enchantments import Enchantment')

    def __send(self, cmd: str):
        logging.info("[jython] send cmd: {}".format(cmd))
        self.__ws.send(cmd)

    # 修改时间
    def time(self, t: int):
        self.__send("time({})".format(t))

    # 打雷
    def bolt(self, name: str):
        self.__send('bolt(lookingat(player("{}")))'.format(name))

    # 爆炸
    def explosion(self, name: str):
        self.__send('explosion(lookingat(player("{}")), power=2)'.format(name))

    # 生成一棵树
    def tree(self, name: str):
        self.__send('tree(lookingat(player("{}")))'.format(name))

    # 生成一个实体
    def swap(self, name: str, entity_id: int):
        self.__send('spawn(lookingat(player("{}")), EntityType.{})'.format(name, entity_enum[entity_id]))

    # 生成方块
    def set_block(self, name: str, material_id: int):
        self.__send('setblock(lookingat(player("{}")), Material.{})'.format(name, material_enum[material_id]))

    # 给予物品
    def give(self, name: str, material_id: int, num: int):
        self.__send(
            'player("{}").getInventory().addItem(ItemStack(Material.{},{}))'.format(name, material_enum[material_id],
                                                                                    num))

    # 给予附魔书
    def enchantment(self, name: str, material_type: int, enchantment_type: int, level: int):
        self.__send(
            'book=ItemStack(Material.{},1);meta=book.getItemMeta();meta.addEnchant(Enchantment.{},{},'
            'True);book.setItemMeta(meta);player("{}").getInventory().addItem(book)'.format(
                material_enum[material_type], enchantment_enum[enchantment_type], level, name))

    def _process_recv(self):
        try:
            data = self.__ws.recv(0.5)
            logging.info("[jython] recv data: {}".format(data.strip()))
        except TimeoutError:
            pass

    def close(self):
        logging.info("on exit")
        self.__ws.close()
