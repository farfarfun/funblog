# funblog

本地笔记发布工具：把本地目录下的 Markdown / Jupyter Notebook（`.md` / `.ipynb`）文件按目录结构扫描成「分类-文章」树，记录到本地 SQLite，再通过 XML-RPC（metaWeblog 协议）批量发布/更新到 [Typecho](https://typecho.org/) 博客。仓库里还带了一个尚未实现的 Yuque（语雀）发布模块的空壳。

## 安装

```bash
pip install funblog
```

从源码安装（开发用）：

```bash
git clone https://github.com/farfarfun/funblog.git
cd funblog
pip install -e .
```

运行时依赖 `fundata`（提供 `SqliteTable` 等基础能力）、`nbformat`、`nbconvert`（用于解析 `.ipynb`）、`farlog`、`tqdm`，均已写入 `pyproject.toml`。`funbuild` 只是发布本包时用到的构建工具，不是运行时依赖，无需单独安装即可使用本包。

## 可离线运行的最小示例

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from funblog.publish.core import BlogManage

with TemporaryDirectory() as directory:
    root = Path(directory) / "笔记"
    category = root / "技术"
    category.mkdir(parents=True)
    (category / "01-第一篇.md").write_text("# 正文\n", encoding="utf-8")

    blog = BlogManage(path_root=str(root), db_path=str(root / "blog.db"))
    blog.local_scan()
    print(blog.page_db.select_all()[0]["title"])  # 第一篇
```

该示例只扫描临时目录并写入临时 SQLite 数据库，不会连接任何远程服务。运行前按上面的安装步骤执行 `pip install funblog`；从源码运行则执行 `pip install -e .`。

## 发布到 Typecho

远程发布需要可访问的 Typecho XML-RPC 地址和一个有发布权限的账号。将凭据放入环境变量，避免写入脚本或仓库：

```bash
export FUNBLOG_TYPECHO_RPC_URL="https://your-blog.example/action/xmlrpc"
export FUNBLOG_TYPECHO_USERNAME="your-username"
export FUNBLOG_TYPECHO_PASSWORD="your-password"
```

```python
import os

from funblog.publish.core import BlogManage

blog = BlogManage(path_root="./notes", db_path="./blog.db")
blog.local_scan()

blog.publish_typecho(
    rpc_url=os.environ["FUNBLOG_TYPECHO_RPC_URL"],
    username=os.environ["FUNBLOG_TYPECHO_USERNAME"],
    password=os.environ["FUNBLOG_TYPECHO_PASSWORD"],
)
```

`BlogManage` 内部用 `BlogCategoryDB` / `BlogPageDB`（均基于 SQLite）记录分类和文章的本地 id 与 Typecho 端 id 的对应关系，重复运行 `local_scan()` + `publish_typecho()` 可以做到增量更新：已发布过的文章会走 `edit_page`，未发布过的走 `new_page`。

仓库中的 `example/publish.py` 使用组织的 `funsecret` 读取同一组凭据。该示例供开发环境使用，先执行 `pip install -e ".[dev]"`（会安装 `funsecret>=1.4.84`），再在 `funsecret` 的密钥存储中配置 `blog/typecho/rpc_url`、`blog/typecho/username` 和 `blog/typecho/password` 三个键后运行。

底层的 Typecho 客户端 `funblog.blog.typecho.Typecho` 封装了 metaWeblog / WordPress 兼容的 XML-RPC 接口（文章、页面、分类、标签、附件、评论），可以单独使用：

```python
import os

from funblog.blog.typecho import Typecho

typecho = Typecho(rpc_url=os.environ["FUNBLOG_TYPECHO_RPC_URL"],
                  username=os.environ["FUNBLOG_TYPECHO_USERNAME"],
                  password=os.environ["FUNBLOG_TYPECHO_PASSWORD"])
print(typecho.get_categories())
```

## 已知局限

- Yuque（语雀）发布模块（`funblog/blog/yuque/`）目前是空文件，功能未实现。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
