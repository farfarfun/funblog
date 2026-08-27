# funblog

本地笔记发布工具：把本地目录下的 Markdown / Jupyter Notebook（`.md` / `.ipynb`）文件按目录结构扫描成「分类-文章」树，记录到本地 SQLite，再通过 XML-RPC（metaWeblog 协议）批量发布/更新到 [Typecho](https://typecho.org/) 博客。仓库里还带了一个尚未实现的 Yuque（语雀）发布模块的空壳，以及一批与博客发布无关的历史遗留爬虫/工具脚本（`noteblog/utils/fzutils`、`noteblog/utils/brush`），目前未被主流程使用，保留仅供参考。

> 注意：包名/导入名是 `noteblog`（历史 `note*` 命名遗留，见 [NAMING.md](https://github.com/farfarfun/todo-list/blob/master/NAMING.md)），与仓库名 `funblog` 不一致。经查 PyPI 上目前**没有**发布 `noteblog` 这个包（404），下面只给出源码安装方式。

## 安装

PyPI 上没有可用的发布包，需要从源码安装：

```bash
git clone https://github.com/farfarfun/funblog.git
cd funblog
pip install -e .
```

依赖 `notebuild`、`notedata`（提供 `SqliteTable` 等基础能力），以及 `nbformat`、`nbconvert`（用于解析 `.ipynb`）。

## 用法示例

```python
from noteblog.publish.core import BlogManage

# path_root: 本地笔记根目录，子目录会被当作分类，.md/.ipynb 文件会被当作文章
blog = BlogManage(path_root='/path/to/notes', db_path='/path/to/blog.db')

# 1. 扫描本地文件，写入分类表/文章表
blog.local_scan()

# 2. 发布到 Typecho（通过 XML-RPC）
blog.publish_typecho(
    rpc_url='https://your-blog.com/action/xmlrpc',
    username='your-username',
    password='your-password',
)
```

`BlogManage` 内部用 `BlogCategoryDB` / `BlogPageDB`（均基于 SQLite）记录分类和文章的本地 id 与 Typecho 端 id 的对应关系，重复运行 `local_scan()` + `publish_typecho()` 可以做到增量更新：已发布过的文章会走 `edit_page`，未发布过的走 `new_page`。

底层的 Typecho 客户端 `noteblog.blog.typecho.Typecho` 封装了 metaWeblog / WordPress 兼容的 XML-RPC 接口（文章、页面、分类、标签、附件、评论），可以单独使用：

```python
from noteblog.blog.typecho import Typecho

typecho = Typecho(rpc_url='https://your-blog.com/action/xmlrpc',
                  username='your-username', password='your-password')
print(typecho.get_categories())
```

## 已知局限

- Yuque（语雀）发布模块（`noteblog/blog/yuque/`）目前是空文件，功能未实现。
- `noteblog/utils/` 下的 `fzutils`、`brush` 是历史爬虫/工具脚本合集，与博客发布主流程无关，未做维护，使用前请自行确认可用性。
