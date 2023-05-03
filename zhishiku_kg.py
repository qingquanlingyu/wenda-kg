from types import NoneType
from plugins.settings import settings
from neo4j import GraphDatabase
import jieba
# encoding=utf-8


class Neo4j:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run(self, cmd):
        with self.driver.session() as session:
            res = session.run(cmd).value()
            return res

    def run_retValue(self, cmd):
        with self.driver.session() as session:
            res = session.run(cmd).value()
            return res

    # 一些自用函数，实际没有用到，如果二次开发可以用用省点时间
    def findLabel_retAttr(self, label, attr):
        with self.driver.session() as session:
            return session.execute_read(self._findLabel_retAttr, label, attr)

    def findName_retAttr(self, name, attr):
        with self.driver.session() as session:
            return session.execute_read(self._findName_retAttr, name, attr)

    def find2Name_retRel(self, val1, val2):
        with self.driver.session() as session:
            res = []
            sres = session.execute_read(
                self._find2Attr_retRel, "name", val1, "name", val2)
            for i in range(len(sres)):
                res.append(sres[i].replace(
                    r"%from", val1).replace(r"%to", val2))
            sres = session.execute_read(
                self._find2Attr_retRel, "name", val2, "name", val1)
            for i in range(len(sres)):
                res.append(sres[i].replace(
                    r"%from", val2).replace(r"%to", val1))
            return res

    def find2Attr_retRel(self, attr1, val1, attr2, val2):
        with self.driver.session() as session:
            res = session.execute_read(
                self._find2Attr_retRel, attr1, val1, attr2, val2)
            return res

    def findARelB_WithBAttr_retB(self, aname, rel, battr, bval):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_WithBAttr_retB, aname, rel, battr, bval)
            return res

    def findARelB_WithAAttr_retA(self, bname, rel, aattr, aval):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_WithAAttr_retA, bname, rel, aattr, aval)
            return res

    def findARelB_retA(self, fname, rel):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_retA, fname, rel)
            return res

    def findARelB_retB(self, fname, rel):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findARelB_retB, fname, rel)
            return res

    def findName_retAllAttr(self, name):
        with self.driver.session() as session:
            res = session.execute_read(
                self._findName_retAllAttr, name)
            return res

    @staticmethod
    def _findLabel_retAttr(tx, label, attr):
        # 通过label查找实体并返回其特定属性
        res = []
        search = f'MATCH (a:{label}) RETURN a.{attr}'
        result = tx.run(search)
        for record in result:
            res.append(record["a."+attr])
        return res

    @staticmethod
    def _findName_retAttr(tx, name, attr):
        # 通过name查找实体并返回其特定属性值
        res = []
        search = f'MATCH (a) WHERE a.name="{name}" RETURN a.{attr}'
        result = tx.run(search)
        for record in result:
            res.append(record["a."+attr])
        return res

    @staticmethod
    def _find2Attr_retRel(tx, attr1, val1, attr2, val2):
        # 通过两个实体的属性查找其关系
        res = []
        search = f'MATCH (a)-[r]->(b) WHERE a.{attr1}="{val1}" AND b.{attr2}="{val2}" RETURN r.note'
        result = tx.run(search)
        for record in result:
            res.append(record["r.note"])
        return res

    @staticmethod
    def _findARelB_retB(tx, fname, rel):
        # 在特定关系类型下，返回某个结点子结点的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE a.name="{fname}" RETURN b.name'
        result = tx.run(search)
        for record in result:
            res.append(record["b.name"])
        return res

    @staticmethod
    def _findARelB_retA(tx, fname, rel):
        # 在特定关系类型下，返回某个结点父结点的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE b.name="{fname}" RETURN a.name'
        result = tx.run(search)
        for record in result:
            res.append(record["a.name"])
        return res

    @staticmethod
    def _findARelB_WithBAttr_retB(tx, aname, rel, battr, bval):
        # 在特定关系类型下，返回某个结点子结点中属性符合要求的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE a.name="{aname}" AND b.{battr}="{bval}" RETURN b.name'
        result = tx.run(search)
        for record in result:
            res.append(record["b.name"])
        return res

    @staticmethod
    def _findARelB_WithAAttr_retA(tx, bname, rel, aattr, aval):
        # 在特定关系类型下，返回某个结点子结点中属性符合要求的结点名
        res = []
        search = f'MATCH (a)-[r:{rel}]->(b) WHERE b.name="{bname}" AND a.{aattr}="{aval}" RETURN a.name'
        result = tx.run(search)
        for record in result:
            res.append(record["a.name"])
        return res

    @staticmethod
    def _findName_retAllAttr(tx, name):
        # 根据结点名，返回所有属性名
        res = []
        search = f'MATCH (n) WHERE n.name="{name}" RETURN properties(n) AS properties'
        result = tx.run(search)
        for record in result:
            res.append(record["properties"])
        return res


with open("plugins/stopwords_txt", encoding="utf-8") as f:
    stopwords = f.read().split('\n')


def remove_stopwords(search_query):
    search_query_without_stopwords = []
    for i in search_query:
        try:
            stopwords.index(i)
        except:
            search_query_without_stopwords.append(i)
    return search_query_without_stopwords


neo = Neo4j(settings.library.kg.Graph_Host,
            settings.library.kg.Graph_User, settings.library.kg.Graph_Password)
entities = neo.run_retValue("MATCH (n) RETURN n.name")
for entity in entities:
    if (type(entity) is not NoneType):
        jieba.add_word(entity)
print("如果更新知识图谱，重启Wenda")


def find(search_query, step=0):
    try:
        knowledge = []  # 查询到的全部相关知识

        search_query = "自由岛是什么"
        search_query = jieba.cut(search_query)
        search_query = remove_stopwords(search_query)
        for entity in search_query:
            if entity in entities:
                # 查找结点属性
                allproperties = neo.run_retValue(
                    f'MATCH (n) WHERE n.name="{entity}" RETURN [labels(n), properties(n)]')
                for properties in allproperties:  # 只会循环一次，除非有同名，那一定是知识图谱的问题
                    labels = "、".join(properties[0])
                    content = f"{entity}的类型是:{labels}。"

                    # knowledge.append({"title": f"{entity}结点标签","content": f"{entity}的类型是:{labels}"})
                    for property in properties[1]:
                        if (property == "name"):
                            content += f"{entity}的名称是:{properties[1][property]}。"
                            # knowledge.append({"title": f"{entity}结点属性","content": f"{entity}的名称是:{properties[1][property]}。"})
                        else:
                            content += f"{entity}的{property}是:{properties[1][property]}。"
                            # knowledge.append({"title": f"{entity}结点属性","content": f"{entity}的{property}是:{properties[1][property]}。"})
                    knowledge.append(
                        {"title": f"{entity}结点", "content": content})

                # 单跳搜索，目前只返回关系所有属性（含标签，名称，不含from、to），相邻结点名称
                all_neighbors_to = neo.run_retValue(
                    f'MATCH (a)-[r]->(b) WHERE a.name="{entity}" RETURN [properties(r), type(r), b.name]')
                for neighbors_to in all_neighbors_to:
                    content = f'{entity}有到{neighbors_to[2]}的关系，关系类型为{neighbors_to[1]}'
                    if ("name" in neighbors_to[0].keys()):
                        content += f'，该关系名称为{neighbors_to[0]["name"]}'
                    for relprops in neighbors_to[0]:
                        if (relprops != "name" and relprops != "from" and relprops != "to"):
                            content += f"，该关系的{relprops}是:{neighbors_to[0][relprops]}"
                    content += "。"
                    knowledge.append({"title": f"{entity}的邻居",
                                      "content": content})

                all_neighbors_from = neo.run_retValue(
                    f'MATCH (b)-[r]->(a) WHERE a.name="{entity}" RETURN [properties(r), type(r), b.name]')
                for neighbors_from in all_neighbors_from:
                    content = f'{entity}有来自{neighbors_from[2]}的关系，关系类型为{neighbors_from[1]}'
                    if ("name" in neighbors_from[0].keys()):
                        content += f'，该关系名称为{neighbors_from[0]["name"]}'
                    for relprops in neighbors_from[0]:
                        if (relprops != "name" and relprops != "from" and relprops != "to"):
                            content += f"，该关系的{relprops}是:{neighbors_from[0][relprops]}"
                    content += "。"
                    knowledge.append({"title": f"{entity}的邻居",
                                      "content": content})
        return [{'title': knowledge[i]['title'], 'content':knowledge[i]['content']}
                for i in range(min(int(settings.library.kg.Count), len(knowledge)))]
    except Exception as e:
        print("知识图谱读取失败", e)
        return []
