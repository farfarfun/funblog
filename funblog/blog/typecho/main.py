from xmlrpc.client import ServerProxy, Fault
from dataclasses import asdict

from .log import logger
from .models import Post, Page, Category, Attachment, Comment


class TypechoPostMixin:
    """文章（Post）相关的 metaWeblog / WordPress 兼容 XML-RPC 接口。"""

    def get_posts(self, num: int = 10) -> list[dict] | None:
        """获取最近 `num` 篇文章。"""
        return self.try_rpc(self.s.metaWeblog.getRecentPosts, num)

    def get_post(self, post_id: int) -> dict | None:
        """按 ID 获取单篇文章。"""
        return self.try_rpc(self.s.metaWeblog.getPost, post_id)

    def new_post(self, post: Post, publish: bool) -> str | None:
        """
        新建一篇文章。

        Post's status will cover publish, and if you only save post, the post id will only be '0'
        If Post's categories are not created, it will only create the first category
        """
        return self.try_rpc(self.s.metaWeblog.newPost, post, publish)

    def edit_post(self, post: Post, post_id: int, publish: bool) -> str | None:
        """编辑一篇已存在的文章。"""
        d = asdict(post)
        d.update({'postId': post_id})
        return self.try_rpc(self.s.metaWeblog.newPost, d, publish)

    def del_post(self, post_id: int) -> None:
        """删除一篇文章。"""
        return self.try_rpc(self.s.blogger.deletePost, post_id)


class TypechoPageMixin:
    """页面（Page）相关的 metaWeblog / WordPress 兼容 XML-RPC 接口。"""

    def get_pages(self) -> list[dict] | None:
        """获取全部页面列表。"""
        return self.try_rpc(self.s.wp.getPages)

    def get_page(self, page_id: int) -> dict | None:
        """
        按 ID 获取单个页面。

        WARNING: Different from other API!
        """
        return self._try_rpc(self.s.wp.getPage, self.blog_id, page_id, self.username, self.password)

    def new_page(self, page: Page, publish: bool) -> str | None:
        """
        新建一个页面。

        Page's status will cover publish, and if you only save post, the post id will only be '0'
        """
        return self.try_rpc(self.s.metaWeblog.newPost, page, publish)

    def edit_page(self, page: Page, page_id: int, publish: bool) -> str | None:
        """编辑一个已存在的页面。"""
        d = asdict(page)
        d.update({'postId': page_id})
        return self.try_rpc(self.s.metaWeblog.newPost, d, publish)

    def del_page(self, page_id: int) -> bool | None:
        """删除一个页面。"""
        return self.try_rpc(self.s.wp.deletePage, page_id)


class TypechoCategoryMixin:
    """分类（Category）相关的 metaWeblog / WordPress 兼容 XML-RPC 接口。"""

    def get_categories(self) -> dict | None:
        """获取全部分类。"""
        return self.try_rpc(self.s.metaWeblog.getCategories)

    def new_category(self, category: Category, parent_id: int = 0) -> str | None:
        """新建一个分类。"""
        return self.try_rpc(self.s.wp.newCategory, category)

    def del_category(self, category_id: int) -> bool | None:
        """删除一个分类。"""
        return self.try_rpc(self.s.wp.deleteCategory, category_id)


class TypechoTagMixin:
    """标签（Tag）相关的 WordPress 兼容 XML-RPC 接口。"""

    def get_tags(self) -> list[dict] | None:
        """获取全部标签。"""
        return self.try_rpc(self.s.wp.getTags)


class TypechoAttachmentMixin:
    """附件/媒体库相关的 WordPress 兼容 XML-RPC 接口。"""

    def get_attachments(self, post_id: int = None, mime_type: str = None, page_size: int = None,
                        page_num: int = None) -> list[dict] | None:
        """按条件筛选并获取媒体库附件列表。"""
        struct = {}
        if post_id:
            struct.update({'parent_id': post_id})
        if mime_type:
            struct.update({'mime_type': mime_type})
        if page_size:
            struct.update({'number': page_size})
        if page_num:
            struct.update({'offset': page_num})
        return self.try_rpc(self.s.wp.getMediaLibrary, struct)

    def get_attachment(self, attachment_id) -> dict | None:
        """按 ID 获取单个附件。"""
        return self.try_rpc(self.s.wp.getMediaItem, attachment_id)

    def new_attachment(self, data: Attachment):
        """上传一个新附件。"""
        return self.try_rpc(self.s.wp.uploadFile, data)


class TypechoCommentMixin:
    """评论（Comment）相关的 WordPress 兼容 XML-RPC 接口。"""

    def get_comments(self, status: str = None, post_id: int = None, page_size: int = None,
                     page_num: int = None) -> list[dict] | None:
        """按条件筛选并获取评论列表。"""
        struct = {}
        if status:
            struct.update({'status': status})
        if post_id:
            struct.update({'parent_id': post_id})
        if page_size:
            struct.update({'number': page_size})
        if page_num:
            struct.update({'offset': page_num})
        return self.try_rpc(self.s.wp.getComments, struct)

    def get_comment(self, comment_id: int) -> dict | None:
        """按 ID 获取单条评论。"""
        return self.try_rpc(self.s.wp.getComment, comment_id)

    def new_comment(self, comment: Comment, post_id: int, comment_parent: str = None) -> None:
        """在指定文章下新建一条评论。"""
        d = asdict(comment)
        if comment_parent:
            d.update({'comment_parent': comment_parent})
        path = post_id
        return self.try_rpc(self.s.wp.newComment, path, d)

    def edit_comment(self, comment: Comment, comment_id: int) -> bool | None:
        """编辑一条已存在的评论。"""
        return self.try_rpc(self.s.wp.editComment, comment_id, comment)

    def del_comment(self, comment_id: int) -> bool | None:
        """删除一条评论。"""
        return self.try_rpc(self.s.wp.deleteComment, comment_id, )


class Typecho(TypechoPostMixin, TypechoPageMixin, TypechoCategoryMixin, TypechoTagMixin, TypechoAttachmentMixin,
              TypechoCommentMixin):
    """
    Typecho 博客的 XML-RPC 客户端，封装 metaWeblog / WordPress 兼容接口。

    通过 `rpc_url`（形如 `https://your-blog.com/action/xmlrpc`）、用户名、密码鉴权后，
    即可调用文章、页面、分类、标签、附件、评论相关方法。
    """

    def __init__(self, rpc_url: str, username: str, password: str):
        """
        :param rpc_url: Typecho 站点的 XML-RPC 调用地址
        :param username: 登录用户名
        :param password: 登录密码
        """
        self.rpc_url = rpc_url
        self.username = username
        self.password = password

        self.s = ServerProxy(rpc_url)
        # blog id could be any number.
        self.blog_id = 1

    def try_rpc(self, rpc_method, *args, **kw):
        """调用 `rpc_method`，自动补上 `blog_id`/`username`/`password` 鉴权参数。"""
        return self._try_rpc(rpc_method, self.blog_id, self.username, self.password, *args, **kw)

    def _try_rpc(self, rpc_method, *args, **kw):
        """
        执行一次 XML-RPC 调用，捕获调用异常并记录带上下文的错误日志。

        :param rpc_method: 要调用的 XML-RPC 方法
        :param args: 透传给 `rpc_method` 的位置参数
        :param kw: 透传给 `rpc_method` 的关键字参数
        :return: RPC 调用结果；调用失败时返回 None
        """
        res = None
        method_name = getattr(rpc_method, "_ServerProxy__name", rpc_method)
        try:
            res = rpc_method(*args, **kw)
            logger.info(res)
            if res == '':
                res = None
        except Fault as e:
            logger.error("Typecho RPC 调用失败，方法：{}，错误码 {}：{}".format(
                method_name, e.faultCode, e.faultString))
        except Exception as e:
            logger.error("Typecho RPC 调用异常，方法：{}，原因：{}".format(method_name, e))
        return res
