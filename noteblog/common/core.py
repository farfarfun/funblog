# coding=utf-8
import os
import string
from time import sleep
from typing import List

import nbformat
import yaml
from nbconvert import MarkdownExporter
from noteblog.core import Category, Post, Typecho
from noteblog.typecho.core import Typecho
from notedata.tables import SqliteTable

from .base import BlogCategoryDB, BlogPageDB, CateDetail, FileTree, PageDetail


def get_all_file(path_root) -> FileTree:
    file_tree = FileTree(os.path.basename(path_root))
    for path in os.listdir(path_root):
        path = os.path.join(path_root, path)

        if os.path.isdir(path):
            filename = os.path.basename(path)
            if filename in ('.ipynb_checkpoints', 'pass') or 'pass' in filename:
                continue
            file_tree.categories.append(get_all_file(path))
        else:
            filename, filetype = os.path.splitext(os.path.basename(path))
            if filetype in ('.ipynb', '.md'):
                file_tree.files.append(path)

    file_tree.files.sort()
    file_tree.categories.sort(key=lambda x: x.name)
    return file_tree


class PostAll:
    def __init__(self, typecho):
        self.typecho: Typecho = typecho
        self.categories = [entry['categoryName']
                           for entry in self.typecho.get_categories()]

    def post(self, path, categories):
        filename, filetype = os.path.splitext(os.path.basename(path))

        post = None
        if filetype == '.ipynb':
            jake_notebook = nbformat.reads(
                open(path, 'r').read(), as_version=4)
            mark = MarkdownExporter()
            content, _ = mark.from_notebook_node(jake_notebook)
            # check title
            if len(jake_notebook.cells) >= 1:
                source = str(jake_notebook.cells[0].source)
                if source.startswith('- '):
                    s = yaml.load(source)
                    res = {}
                    [res.update(i) for i in s]

                    title = res.get("title", filename)
                    tags = res.get("tags", '')
                    tmp_categories = categories or res.get(
                        "category", '').split(',')
                    tmp_categories = categories

                    del jake_notebook.cells[0]
                    content, _ = mark.from_notebook_node(jake_notebook)
                    post = Post(title=title,
                                description=content,
                                mt_keywords=tags,
                                categories=tmp_categories, )

            post = post or Post(title=self.name_convent(filename),
                                description=content,
                                categories=categories, )
        elif filetype == '.md':
            content = open(path, 'r').read()
            post = Post(title=self.name_convent(filename),
                        description=content,
                        categories=categories, )
        else:
            print("error {}".format(filetype))
            return

        self.typecho.new_post(post, publish=True)

    def name_convent(self, name: str) -> str:
        return name.lstrip(string.digits).lstrip('|_-|.')

    def category_manage(self, category, parent_id=0):
        category = self.name_convent(category)

        cate = Category(name=category, parent=parent_id)
        return category, int(self.typecho.new_category(cate))

    def post_tree(self, file_tree: FileTree, categories, parent_id=0):
        if len(file_tree.files) == 0 and len(file_tree.categories) == 0:
            return

        categories, parent_id = self.category_manage(
            file_tree.name, parent_id=parent_id)

        for path in file_tree.files:
            self.post(path, categories=[categories])
            sleep(1)
        for tree in file_tree.categories:
            if "pass" in tree.name:
                continue
            self.post_tree(tree, categories=tree.name, parent_id=parent_id)

    def post_all(self, path_root):
        res = get_all_file(path_root)

        for path in res.categories:
            self.post_tree(path, categories=path.name, parent_id=0)
            # break


class BlogManage:
    def __init__(self, path_root):
        self.cate_db = BlogCategoryDB()
        self.page_db = BlogPageDB()
        self.path_root = path_root

    def insert_cate(self, tree: FileTree, parent_info: dict) -> dict:
        properties = {'describe': tree.name}
        condition = {'cate_name': tree.name,
                     'parent_id': parent_info['cate_id']}
        properties.update(condition)
        self.cate_db.update_or_insert(
            properties=properties, condition=condition)

        return self.cate_db.select(condition=condition)[0]

    def insert_page(self, properties: dict, cate_info: dict):
        page = PageDetail()
        page.insert_page(file_info=properties, cate_info=cate_info)
        properties.update(page.to_dict())

        condition = {
            'title': properties['title'],
            'cate_id': properties['cate_id']
        }

        self.page_db.update_or_insert(
            properties=properties, condition=condition)

        return self.page_db.select(condition=condition)[0]

    def create_cate(self, tree: FileTree, parent_info: dict):
        parent_info = self.insert_cate(tree, parent_info)

        for file in tree.categories:
            self.create_cate(file, parent_info)

        for file in tree.files:
            self.insert_page({'path': file}, parent_info)

    def run(self):
        files = get_all_file(path_root=self.path_root)
        tree_root = {'cate_id': 0, 'cate_name': '根目录'}
        for f in files.categories:
            self.create_cate(f, tree_root)
