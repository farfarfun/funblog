from funblog.blog.typecho import Typecho
from funblog.blog.typecho.models import Category as TypeCate
from funblog.blog.typecho.models import Post as TypePost
from funblog.core.meta import CateDetail as Cate
from funblog.core.meta import PageDetail as Page

from .core import PublishBase


class TypechoPB(PublishBase):
    """将通用发布接口适配到 Typecho 客户端。"""

    def __init__(self, typecho: Typecho, *args, **kwargs) -> None:
        """初始化适配器。"""
        super().__init__(*args, **kwargs)
        self.typecho: Typecho = typecho

    @staticmethod
    def page_transform(page: Page) -> TypePost:
        """将本地文章转换为 Typecho 文章。"""
        type_page = TypePost(
            title=page.title,
            description=page.content,
            categories=[page.cate_name],
        )
        return type_page

    @staticmethod
    def cate_transform(cate: Cate) -> TypeCate:
        """将本地分类转换为 Typecho 分类。"""
        type_cate = TypeCate(name=cate.cate_name, parent=cate.parent_id)
        return type_cate

    def get_pages(self, nums: int = 10, *args, **kwargs) -> list[dict] | None:
        """获取远程文章。"""
        return self.typecho.get_pages()

    def get_page(self, page_id: int, *args, **kwargs) -> dict | None:
        """获取远程文章详情。"""
        return self.typecho.get_page(page_id)

    def new_page(self, page: Page, *args, **kwargs) -> str | None:
        """创建远程文章。"""
        return self.typecho.new_post(self.page_transform(page), True)

    def edit_page(self, page_id: int, page: Page, *args, **kwargs) -> str | None:
        """更新远程文章。"""
        return self.typecho.edit_post(self.page_transform(page), page_id, True)

    def del_page(self, page_id: int, *args, **kwargs) -> None:
        """删除远程文章（当前 Typecho 适配器未实现）。"""

    def get_cates(self, nums: int = 10, *args, **kwargs) -> dict | None:
        """获取远程分类。"""
        return self.typecho.get_categories()

    def get_cate(self, cate_id: int, *args, **kwargs) -> dict | None:
        """获取远程分类详情。"""
        return self.typecho.get_categories()

    def new_cate(self, cate: Cate, *args, **kwargs) -> str | None:
        """创建远程分类。"""
        return self.typecho.new_category(
            self.cate_transform(cate), parent_id=cate.parent_id
        )

    def edit_cate(self, cate_id: int, cate: Cate, *args, **kwargs) -> None:
        """更新远程分类（当前 Typecho 适配器未实现）。"""

    def del_cate(self, cate_id: int, *args, **kwargs) -> None:
        """删除远程分类（当前 Typecho 适配器未实现）。"""
