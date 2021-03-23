# coding=utf-8
import os

from noteblog.blog.typecho import Typecho
from noteblog.core.base import PublishBase
from noteblog.core.meta import (BlogCategoryDB, BlogPageDB, CateDetail,
                                FileTree, PageDetail)
from noteblog.publish.typecho import TypechoPB
from tqdm import tqdm


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

        is_update = False
        condition = {}
        if page.page_uid is not None:
            condition = {"page_uid": page.page_uid}
            up = self.page_db.update(properties, condition)
            if up.rowcount > 0:
                is_update = True
        if not is_update:
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

    def publish_cate(self, blog: PublishBase, key='cate_typecho_id'):
        for cate in tqdm(self.cate_db.select_all()):
            if cate[key] <= 0:
                parent_id = cate['parent_id']
                if parent_id != 0:
                    res = self.cate_db.select(condition={'cate_id': parent_id})
                    if len(res) > 0:
                        cate['parent_id'] = res[0][key]
                _cate = CateDetail(**cate)
                cate_id = blog.new_cate(_cate)
                cate[key] = cate_id
                self.cate_db.update(
                    cate, condition={'cate_id': cate['cate_id']})

    def publish_page(self, blog: PublishBase, key='page_typecho_id'):
        for page in tqdm(self.page_db.select_all()):
            if page[key] <= 0:
                _page = PageDetail(**page)
                page_id = blog.new_page(_page)
                page[key] = page_id
                self.page_db.update(
                    page, condition={'page_id': page['page_id']})
            else:
                _page = PageDetail(**page)
                blog.edit_page(page_id=_page[key], page=_page)

    def publish_typecho(self, rpc_url: str, username: str, password: str):
        typecho = Typecho(rpc_url=rpc_url, username=username,
                          password=password)
        typecho_pb = TypechoPB(typecho)
        self.publish_cate(typecho_pb, key='cate_typecho_id')
        self.publish_page(typecho_pb, key='page_typecho_id')
