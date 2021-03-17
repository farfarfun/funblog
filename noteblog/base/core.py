from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional

from.meta import Cate, Page


class PublishBase(meteaclass=ABCMeta):
    def __init__(self, name='default', *args, **kwargs):
        self.name = name

    @abstractmethod
    def get_pages(self, nums=10, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def get_page(self, page_id, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def new_page(self, page: Page, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def edit_page(self, page_id, page: Page, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def del_page(self, page_id, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def get_cates(self, nums=10, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def get_cate(self, cate_id, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def new_cate(self, cate: Cate, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def edit_cate(self, cate_id, cate: Cate, *args, **kwargs):
        raise Exception("not implement")

    @abstractmethod
    def del_cate(self, cate_id, *args, **kwargs):
        raise Exception("not implement")
