from .main import Typecho
from .models import Attachment, Category, Comment, Page, Post

name = 'pytypecho'

__all__ = ['Typecho', 'Post', 'Page', 'Category', 'Attachment', 'Comment']


"""

Typecho的XML-RPC调用地址为http://xx.com/action/xmlrpc，接口见代码：https://github.com/typecho/typecho/blob/master/var/Widget/XmlRpc.php#L2249-L2322

Typecho的XML-RPC调用和WordPress调用方法是一样的，只是调用地址不一样而已，所以你可以参考WordPress的相关教程，这里给出一篇范例：http://code.tutsplus.com/articles/xml-rpc-in-wordpress--wp-25467


https://github.com/veoco/PyTypecho
"""
