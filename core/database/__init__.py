import chromadb
import uuid
from chromadb.utils import embedding_functions
from core.base import Base
import enum


# 文本类型
class TextType(enum.Enum):
    Entity = "entity"  # 实体id
    Material = "material"  # 物品id
    Brewing = "brewing"  # 炼药知识
    Command = "command"  # 我的世界指令
    Enchantment = "enchantment"  # 附魔


class ChromadbDb:
    def __init__(self):
        self.base = Base()
        self.__chroma_client = chromadb.PersistentClient(path="db")
        self.__collection = self.__chroma_client.get_or_create_collection(
            name="embedding",
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_base=self.base.openapi_base,
                api_key=self.base.openapi_key,
                model_name="text-embedding-ada-002",
            ))

    # 添加文本
    def add_content(self, text: str, text_type: TextType):
        self.__collection.add(
            documents=[text],
            metadatas=[{"type": text_type.value}],
            ids=[uuid.uuid4().hex]
        )

    def query_content(self, query: str, result: int):
        results = self.__collection.query(
            query_texts=[query],
            n_results=result
        )
        return results

    def get_data(self, no: int, size: int) -> [int, dict]:
        count = self.__collection.count()
        result = self.__collection.get(limit=size, offset=(no - 1) * size)
        return count, result

    def delete_data(self, ids: list[str]):
        self.__collection.delete(ids=ids)
