from abc import abstractmethod

from .meta import CateDetail as Cate
from .meta import PageDetail as Page


class PublishBase(object):
    """
    发布渠道的抽象基类。

    各发布渠道（如 Typecho、语雀）需继承本类并实现全部文章 / 分类相关方法。
    未实现的方法调用时会抛出 ``NotImplementedError``。
    """

    def __init__(self, name='default', *args, **kwargs):
        """
        :param name: 发布渠道名称，用于区分不同的发布目标
        """
        self.name = name

    @abstractmethod
    def get_pages(self, nums=10, *args, **kwargs):
        """获取文章列表，子类必须实现。"""
        raise NotImplementedError("get_pages 未实现")

    @abstractmethod
    def get_page(self, page_id, *args, **kwargs):
        """按 ID 获取单篇文章，子类必须实现。"""
        raise NotImplementedError("get_page 未实现")

    @abstractmethod
    def new_page(self, page: Page, *args, **kwargs):
        """新建一篇文章，子类必须实现。"""
        raise NotImplementedError("new_page 未实现")

    @abstractmethod
    def edit_page(self, page_id, page: Page, *args, **kwargs):
        """编辑一篇已存在的文章，子类必须实现。"""
        raise NotImplementedError("edit_page 未实现")

    @abstractmethod
    def del_page(self, page_id, *args, **kwargs):
        """删除一篇文章，子类必须实现。"""
        raise NotImplementedError("del_page 未实现")

    @abstractmethod
    def get_cates(self, nums=10, *args, **kwargs):
        """获取分类列表，子类必须实现。"""
        raise NotImplementedError("get_cates 未实现")

    @abstractmethod
    def get_cate(self, cate_id, *args, **kwargs):
        """按 ID 获取单个分类，子类必须实现。"""
        raise NotImplementedError("get_cate 未实现")

    @abstractmethod
    def new_cate(self, cate: Cate, *args, **kwargs):
        """新建一个分类，子类必须实现。"""
        raise NotImplementedError("new_cate 未实现")

    @abstractmethod
    def edit_cate(self, cate_id, cate: Cate, *args, **kwargs):
        """编辑一个已存在的分类，子类必须实现。"""
        raise NotImplementedError("edit_cate 未实现")

    @abstractmethod
    def del_cate(self, cate_id, *args, **kwargs):
        """删除一个分类，子类必须实现。"""
        raise NotImplementedError("del_cate 未实现")
