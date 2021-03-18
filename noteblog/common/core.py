# coding=utf-8
import os
import string
from time import sleep

import nbformat
import yaml
from nbconvert import MarkdownExporter
from noteblog.common.base import (BlogCategoryDB, BlogPageDB, FileTree,
                                  PageDetail)


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


class BlogManage:
    def __init__(self, path_root, db_path=None):
        self.cate_db = BlogCategoryDB(db_path=db_path)
        self.page_db = BlogPageDB(db_path=db_path)
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

    def local_scan_category(self, tree: FileTree, parent_info: dict):
        parent_info = self.insert_cate(tree, parent_info)

        for file in tree.categories:
            self.local_scan_category(file, parent_info)

        for file in tree.files:
            self.insert_page({'path': file}, parent_info)

    def local_scan(self):
        files = get_all_file(path_root=self.path_root)
        tree_root = {'cate_id': 0, 'cate_name': '根目录'}
        for f in files.categories:
            self.local_scan_category(f, tree_root)

    def copy_category(self, copy_fun):
        for cate in self.cate_db.select_all():
            print(cate)
