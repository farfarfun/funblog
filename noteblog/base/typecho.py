from noteblog.base.core import PublishBase
from noteblog.base.meta import Cate, Page
from noteblog.blog.typecho import Typecho
from noteblog.blog.typecho.models import Category as TypeCate
from noteblog.blog.typecho.models import Page as TypePage


class TypechoPB(PublishBase):
    def __init__(self, typecho, *args, **kwargs):
        super(TypechoPB, self).__init__(*args, **kwargs)
        self.typecho: Typecho = typecho

    @staticmethod
    def page_transform(page: Page) -> TypePage:
        type_page = TypePage(
            title=page.title,
            description=page.description,
            # categories=[],
        )
        return type_page

    @staticmethod
    def cate_transform(cate: Cate) -> TypeCate:
        type_cate = TypeCate(
            name=cate.cate_name,
            parent=cate.parent_id
        )
        return type_cate

    def get_pages(self, nums=10, *args, **kwargs):
        return self.typecho.get_pages()

    def get_page(self, page_id, *args, **kwargs):
        return self.typecho.get_page(page_id)

    def new_page(self, page: Page, *args, **kwargs):
        return self.typecho.new_page(self.page_transform(page), True)

    def edit_page(self, page_id, page: Page, *args, **kwargs):
        return self.typecho.edit_page(self.page_transform(page), page_id, True)

    def del_page(self, page_id, *args, **kwargs):
        pass

    def get_cates(self, nums=10, *args, **kwargs):
        return self.typecho.get_categories()

    def get_cate(self, cate_id, *args, **kwargs):
        return self.typecho.get_categories()

    def new_cate(self, cate: Cate, *args, **kwargs):
        return self.typecho.new_category(self.cate_transform(cate), parent_id=cate.parent_id)

    def edit_cate(self, cate_id, cate: Cate, *args, **kwargs):
        pass

    def del_cate(self, cate_id, *args, **kwargs):
        pass
