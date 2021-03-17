from typing import Dict, List, Optional

from.meta import Cate, Page


class PublishBase:
    def __init__(self, name='default', *args, **kwargs):
        self.name = name

    def get_pages(self, *args, **kwargs):
        raise Exception("not implement")

    def get_page(self, page_id, *args, **kwargs):
        raise Exception("not implement")

    def new_page(self, page: Page, *args, **kwargs):
        raise Exception("not implement")

    def edit_page(self, page_id, page: Page, *args, **kwargs):
        raise Exception("not implement")

    def del_page(self, page_id, *args, **kwargs):
        raise Exception("not implement")

    def get_cates(self, *args, **kwargs):
        raise Exception("not implement")

    def get_cate(self, cate_id, *args, **kwargs):
        raise Exception("not implement")

    def new_cate(self, cate: Cate, *args, **kwargs):
        raise Exception("not implement")

    def edit_cate(self, cate_id, cate: Cate, *args, **kwargs):
        raise Exception("not implement")

    def del_cate(self, cate_id, *args, **kwargs):
        raise Exception("not implement")
