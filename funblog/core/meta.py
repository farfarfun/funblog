# coding=utf-8
import os
import string
import uuid

import nbformat
from farlog import getLogger
from nbconvert import MarkdownExporter
from fundata.tables_bak import SqliteTable

logger = getLogger("funblog")


class CateDetail:
    """分类详情，对应本地 SQLite 分类表的一行记录，以及各发布渠道的分类 ID 映射。"""

    def __init__(self, *args, **kwargs):
        self.cate_id = None
        self.cate_name = None
        self.describe = None
        self.parent_id = None
        self.parent_name = None
        self.cate_typecho_id = None
        self.cate_yuque_id = None
        self.from_dict(kwargs)

    def from_dict(self, properties: dict):
        """用字典批量更新实例属性。"""
        self.__dict__.update(properties)

    def to_dict(self):
        """导出实例属性为字典，便于写入数据库。"""
        result = {}
        result.update(self.__dict__)
        return result


class PageDetail:
    """文章详情，对应本地 SQLite 文章表的一行记录，负责本地文件的读写与头部元信息解析。"""

    def __init__(self, *args, **kwargs):
        self.page_id = 0
        self.page_uid = ""
        self.title = ''
        self.sub_title = ''
        self.describe = ''
        self.cate_id = 0
        self.cate_name = ''
        self.page_typecho_id = 0
        self.page_yuque_id = 0
        self.path = ''
        self.tags = ''
        self.modify_time = ""
        self.create_time = ""

        self.from_dict(kwargs)

    def from_dict(self, properties: dict):
        """用字典批量更新实例属性。"""
        self.__dict__.update(properties)

    def to_dict(self):
        """导出实例属性为字典（不含自增主键 `page_id`），便于写入数据库。"""
        result = {}
        result.update(self.__dict__)
        result.pop('page_id')
        return result

    def reads(self):
        """读取 `self.path` 指向的本地文件全文内容。"""
        return open(self.path, 'r').read()

    def writes(self, s):
        """将内容整体写回 `self.path` 指向的本地文件（覆盖写）。"""
        with open(self.path, 'w') as f:
            f.write(s)

    @staticmethod
    def name_convent(name: str) -> str:
        """去掉文件名前导的排序数字与分隔符，得到用作文章标题的干净名称。"""
        return name.lstrip(string.digits).lstrip('|_-|.')

    def _head_info_str(self):
        """把标题/标签/uid 等字段序列化为写回文件头部的 Markdown 列表文本。"""
        head_info = {}
        if self.title is not None:
            head_info['title'] = self.title.strip()
        if self.tags is not None:
            head_info['tags'] = ','.join(self.tags)
        if self.page_uid is not None:
            head_info['uid'] = self.page_uid.replace('-', '').strip()

        return '\n'.join(['- {}: {}'.format(k, v.strip()) for k, v in head_info.items()])

    def _head_info_parse(self, info: str = None):
        """解析文件头部形如 `- key: value` 的元信息文本，回填到实例属性。"""
        head_info = {}
        if info is None:
            return
        for line in info.split("\n"):
            line = line.strip()
            if line.startswith('-'):
                line = line[1:].strip()

                if ':' in line:
                    i = line.index(':')
                    key, value = line[:i], line[i + 1:]
                    head_info[key] = value
        if 'uid' in head_info.keys():
            self.page_uid = head_info['uid'].replace('-', '').strip()
        if 'title' in head_info.keys():
            self.title = head_info['title'].strip()
        if 'tags' in head_info.keys():
            self.tags = head_info['tags'].strip()
        if 'author' in head_info.keys():
            self.author = head_info['author'].strip()
        if 'create_time' in head_info.keys():
            self.create_time = head_info['create_time'].strip()
        if 'modify_time' in head_info.keys():
            self.modify_time = head_info['modify_time'].strip()
        return head_info

    def _read_ipynb(self, insert_mark=True, fill_mark=True):
        """将 `self.path` 指向的 `.ipynb` 文件转换为 Markdown 正文，并按需解析/回写头部元信息。"""
        mark = MarkdownExporter()
        jake_notebook = nbformat.reads(
            open(self.path, 'r').read(), as_version=4)
        content, _ = mark.from_notebook_node(jake_notebook)
        if len(jake_notebook.cells) == 0:
            return content

        source = str(jake_notebook.cells[0].source)

        # 导入头部定义的变量
        if source.startswith('- '):
            try:
                self._head_info_parse(source)
                del jake_notebook.cells[0]
                content, _ = mark.from_notebook_node(jake_notebook)
            except Exception as e:
                logger.error("解析 ipynb 头部元信息失败，文件：{}，原因：{}".format(self.path, e))

        # 信息补全
        if (source.startswith('- ') and fill_mark) or (not source.startswith('- ') and insert_mark):
            cell = jake_notebook.cells[0].copy()
            cell.source = self._head_info_str()
            cell.cell_type = 'markdown'
            cell.id = 'tribal-finnish'

            jake_notebook.cells.insert(0, cell)
            self.writes(nbformat.writes(jake_notebook))

        return content

    @property
    def content(self):
        """本文章的正文内容（Markdown 文本），按需解析 `.md`/`.ipynb`。"""
        return self.init_page()

    def init_page(self):
        """根据 `self.path` 的文件名/扩展名初始化标题、UID，并解析出正文内容。"""
        filename, filetype = os.path.splitext(os.path.basename(self.path))

        self.title = self.name_convent(filename)
        self.page_uid = str(uuid.uuid1()).replace('-', '')

        if filetype == '.ipynb':
            content = self._read_ipynb()
        elif filetype == '.md':
            content = open(self.path, 'r').read()
        else:
            # raise NotImplementedError("error {}".format(filetype))
            content = ""

        return content

    def insert_page(self, file_info: dict, cate_info: dict = None):
        """
        根据本地扫描得到的文件信息与所属分类信息填充文章字段。

        :param file_info: 至少包含 `path`（本地文件路径）的字典
        :param cate_info: 至少包含 `cate_id`、`cate_name` 的分类信息字典
        """
        self.path = file_info['path']
        self.cate_id = cate_info['cate_id']
        self.cate_name = cate_info['cate_name']

        self.init_page()


class BlogCategoryDB(SqliteTable):
    """分类表的本地 SQLite 存储，记录本地分类与各发布渠道分类 ID 的映射关系。"""

    def __init__(self, table_name='cate_table', db_path=None, *args, **kwargs):
        if db_path is None:
            db_path = os.path.abspath(os.path.dirname(__file__)) + '/blog.db'
        columns = ['cate_id', 'cate_name', 'describe', 'parent_id',
                   'parent_name', 'cate_typecho_id', 'cate_yuque_id']
        super(BlogCategoryDB, self).__init__(db_path=db_path,
                                             table_name=table_name, columns=columns, *args, **kwargs)
        self.create()

    def create(self):
        """建表（若不存在）。"""
        self.execute("""
                create table if not exists {} (
                cate_id             integer       primary key AUTOINCREMENT
               ,cate_name           varchar(200)  DEFAULT ('')
               ,describe            varchar(5000) DEFAULT ('')
               ,parent_id           integer       DEFAULT (-1)
               ,parent_name         varchar(200)  DEFAULT ('')
               ,cate_typecho_id     integer       DEFAULT (-1)
               ,cate_yuque_id       integer       DEFAULT (-1)
        )
        """.format(self.table_name))

    def update(self, properties: dict, condition: dict = None):
        """按 `condition` 更新分类记录。"""
        condition = condition or {}
        # condition.update({'cate_id': properties['cate_id']})

        return super(BlogCategoryDB, self).update(properties, condition)

    def insert(self, properties: dict):
        """插入一条分类记录。"""
        return super(BlogCategoryDB, self).insert(properties)


class BlogPageDB(SqliteTable):
    """文章表的本地 SQLite 存储，记录本地文章与各发布渠道文章 ID 的映射关系。"""

    def __init__(self, table_name='page_table', db_path=None, *args, **kwargs):
        if db_path is None:
            db_path = os.path.abspath(os.path.dirname(__file__)) + '/blog.db'
        columns = ['page_id', 'page_uid', 'title', 'sub_title', 'describe', 'cate_id', 'cate_name',
                   'page_typecho_id', 'page_yuque_id', 'path', 'tags']
        super(BlogPageDB, self).__init__(db_path=db_path,
                                         table_name=table_name, columns=columns, *args, **kwargs)
        self.create()

    def create(self):
        """建表（若不存在）。"""
        self.execute("""
                create table if not exists {} (
                page_id             integer       primary key AUTOINCREMENT
               ,page_uid            varchar(200)   DEFAULT ('')
               ,title               varchar(200)   DEFAULT ('')
               ,sub_title           varchar(200)   DEFAULT ('')
               ,describe            varchar(50000) DEFAULT ('')
               ,cate_id             integer        DEFAULT (-1)
               ,cate_name           varchar(200)   DEFAULT ('')
               ,page_typecho_id     integer        DEFAULT (-1)
               ,page_yuque_id       integer        DEFAULT (-1)
               ,path                varchar(2000)  DEFAULT ('')
               ,tags                varchar(2000)  DEFAULT ('')
        )
        """.format(self.table_name))

    def update(self, properties: dict, condition: dict = None):
        """按 `condition` 更新文章记录。"""
        condition = condition or {}
        # condition.update({'cate_id': properties['cate_id']})

        return super(BlogPageDB, self).update(properties, condition)

    def insert(self, properties: dict):
        """插入一条文章记录。"""
        return super(BlogPageDB, self).insert(properties)


class FileTree:
    """本地目录扫描结果的树形结构：一个分类节点，含子分类与本分类下的文件路径列表。"""

    def __init__(self, name="默认分类"):
        self.name: str = name
        self.categories: list["FileTree"] = []
        self.files: list[str] = []

    def __str__(self):
        return "{}  {}  {}".format(self.name, ';'.join([i.__str__() for i in self.categories]), len(self.files))
