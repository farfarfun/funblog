# coding=utf-8
import os
import string
import uuid
from typing import List

import nbformat
from nbconvert import MarkdownExporter
from notedata.tables import SqliteTable


class CateDetail:
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
        self.__dict__.update(properties)

    def to_dict(self):
        result = {}
        result.update(self.__dict__)
        return result


class PageDetail:
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
        self.__dict__.update(properties)

    def to_dict(self):
        result = {}
        result.update(self.__dict__)
        result.pop('page_id')
        return result

    def reads(self):
        return open(self.path, 'r').read()

    def writes(self, s):
        with open(self.path, 'w') as f:
            f.write(s)

    @staticmethod
    def name_convent(name: str) -> str:
        return name.lstrip(string.digits).lstrip('|_-|.')

    def _head_info_str(self):
        head_info = {}
        if self.title is not None:
            head_info['title'] = self.title
        if self.tags is not None:
            head_info['tags'] = ','.join(self.tags)
        if self.page_uid is not None:
            head_info['uid'] = self.page_uid.replace('-', '')

        return '\n'.join(['- {}: {}'.format(k, v) for k, v in head_info.items()])

    def _head_info_parse(self, info: str = None):
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
            self.page_uid = head_info['uid'].replace('-', '')
        if 'title' in head_info.keys():
            self.title = head_info['title']
        if 'tags' in head_info.keys():
            self.tags = head_info['tags']
        if 'author' in head_info.keys():
            self.author = head_info['author']
        if 'create_time' in head_info.keys():
            self.create_time = head_info['create_time']
        if 'modify_time' in head_info.keys():
            self.modify_time = head_info['modify_time']
        return head_info

    def _read_ipynb(self, insert_mark=True, fill_mark=True):
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
                print("error 11111 : {}".format(e))

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
        return self.init_page()

    def init_page(self):
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
        self.path = file_info['path']
        self.cate_id = cate_info['cate_id']
        self.cate_name = cate_info['cate_name']

        self.init_page()


class BlogCategoryDB(SqliteTable):
    def __init__(self, table_name='cate_table', db_path=None, *args, **kwargs):
        if db_path is None:
            db_path = os.path.abspath(os.path.dirname(__file__)) + '/blog.db'
        columns = ['cate_id', 'cate_name', 'describe', 'parent_id',
                   'parent_name', 'cate_typecho_id', 'cate_yuque_id']
        super(BlogCategoryDB, self).__init__(db_path=db_path,
                                             table_name=table_name, columns=columns, *args, **kwargs)
        self.create()

    def create(self):
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
        condition = condition or {}
        # condition.update({'cate_id': properties['cate_id']})

        return super(BlogCategoryDB, self).update(properties, condition)

    def insert(self, properties: dict):
        return super(BlogCategoryDB, self).insert(properties)


class BlogPageDB(SqliteTable):
    def __init__(self, table_name='page_table', db_path=None, *args, **kwargs):
        if db_path is None:
            db_path = os.path.abspath(os.path.dirname(__file__)) + '/blog.db'
        columns = ['page_id', 'page_uid', 'title', 'sub_title', 'describe', 'cate_id', 'cate_name',
                   'page_typecho_id', 'page_yuque_id', 'path', 'tags']
        super(BlogPageDB, self).__init__(db_path=db_path,
                                         table_name=table_name, columns=columns, *args, **kwargs)
        self.create()

    def create(self):
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
        condition = condition or {}
        # condition.update({'cate_id': properties['cate_id']})

        return super(BlogPageDB, self).update(properties, condition)

    def insert(self, properties: dict):
        return super(BlogPageDB, self).insert(properties)


class FileTree:
    def __init__(self, name="默认分类"):
        self.name: str = name
        self.categories: List[FileTree] = []
        self.files: List[str] = []

    def __str__(self):
        return "{}  {}  {}".format(self.name, ';'.join([i.__str__() for i in self.categories]), len(self.files))
