from dataclasses import dataclass, field
from xmlrpc.client import Binary


@dataclass
class Meta:
    name: str
    parent: int = 0
    slug: str = ""
    description: str = ""


@dataclass
class Category(Meta):
    pass


@dataclass
class Tag(Meta):
    pass


@dataclass
class Content:
    """
    文章或页面的通用内容。

    文章至少需要 ``title``、``description`` 和分类；页面至少需要前两项。
    Typecho 会用 ``<!--more-->`` 连接 ``description`` 与 ``mt_text_more``；标签应以逗号分隔，
    ``created`` 为时间戳，``post_status`` 可为 ``publish``、``save`` 或 ``private``。
    """

    title: str
    description: str

    slug: str = ""
    mt_text_more: str = ""
    wp_password: str = ""
    mt_keywords: str = ""
    created: str = ""
    mt_allow_comments: int = 1
    mt_allow_pings: int = 1
    post_status: str = ""


@dataclass
class Post(Content):
    post_type: str = "post"
    categories: list[str] = field(default_factory=list)


@dataclass
class Page(Content):
    post_type: str = "page"
    wp_page_order: int = 0
    wp_page_template: str = ""


@dataclass
class Attachment:
    """
    上传到媒体库的附件。

    :param name: 文件名，Typecho 用它的扩展名判断文件类型，不能为空
    :param bytes: 文件内容。必须是 `xmlrpc.client.Binary`（或 `bytes`），
        XML-RPC 会编码为 base64 传输；传文件对象无法序列化。
    """

    name: str
    bytes: Binary


@dataclass
class Comment:
    content: str

    author: str = ""
    author_email: str = ""
    author_url: str = ""

    comment_author: int = 0
    comment_author_email: int = 0
    comment_author_url: int = 0

    def __post_init__(self) -> None:
        if self.author:
            self.comment_author = 1
        if self.author_email:
            self.comment_author_email = 1
        if self.author_url:
            self.comment_author_url = 1
