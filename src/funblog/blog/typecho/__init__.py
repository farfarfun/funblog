"""
Typecho 博客的 XML-RPC 客户端。

调用地址形如 `https://your-blog.com/action/xmlrpc`，接口定义见 Typecho 源码
`var/Widget/XmlRpc.php`。Typecho 实现的是 metaWeblog / WordPress 兼容接口，
因此 WordPress 的 XML-RPC 教程同样适用。
"""

from .main import Typecho
from .models import Attachment, Category, Comment, Page, Post

__all__ = ["Attachment", "Category", "Comment", "Page", "Post", "Typecho"]
