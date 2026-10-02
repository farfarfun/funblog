# 更新日志

本文件记录 `funblog` 的版本变更，按版本倒序排列。

## [0.6.0]（当前版本）

首个发布到 PyPI 的版本：`pip install funblog`。

### 新增

- 公开 API 的行为测试：Typecho 各 XML-RPC 方法的实参顺序、模型的 XML-RPC 可序列化性、
  头部元信息解析与回写、目录扫描结果（`tests/test_public_api.py`）。
- `[tool.ruff]` 配置（`target-version = "py310"`），`ruff check` / `ruff format --check` 全绿。

### 变更

- 破坏性变更：删除历史遗留模块 `funblog.utils`（`pyblog`、`blog2`）。
  - 这两个模块是 Python 2 时代的 metaWeblog 脚本，早已无法在 Python 3 下运行
    （`Blog.execute` 把参数当成单个元组传给服务端、`MetaWeblog.__init__` 把
    `app_key` 和 `default_blog_id` 传反、`f.func_name`、`str.decode`、
    `MovableType._parse_custom_fields` 里的 `__name_` 拼写错误等），
    且包内没有任何地方引用它们。
  - 迁移方法：改用 `funblog.blog.typecho.Typecho`，它实现了同一套
    metaWeblog / WordPress 兼容接口并有测试覆盖。
- 破坏性变更：删除历史遗留的爬虫/工具脚本集合 `funblog.utils.fzutils`、`funblog.utils.brush`
  与 `funblog.utils.test`。它们与博客发布主流程无关、长期无人维护，依赖
  （`selenium`、`scrapy`、`celery`、`demjson`、`execjs`、`gevent`、`scapy` 等）
  从未写进 `pyproject.toml`，且 `funblog/utils/test.py` 在模块顶层就发起网络请求、
  启动多进程，导入即有副作用。无替代实现。
- 依赖口径按「源码实际 import」收紧：
  - `fundata` 下限提到 `>=1.0.4`：`fundata 1.0.1` 的 `fundata.tables_bak` 用了 `pandas`
    却没声明，按旧下限装出来的环境 `import funblog.core.meta` 会直接
    `ModuleNotFoundError: pandas`；1.0.4 自己声明了 `pandas`。
  - 移除 `pandas`、`funshell`：源码并不直接 import，由 `fundata` 自己声明。
  - `funsecret` 从运行时依赖移到 dev 组：只有 `example/publish.py` 在用。
- `Attachment.bytes` 的类型标注由 `BinaryIO` 改为 `xmlrpc.client.Binary`：文件对象无法被
  XML-RPC 序列化，附件内容必须是 `Binary`（或 `bytes`）。
- 清理 `funblog.blog.typecho` 的包初始化：删除无用的模块级变量 `name = 'pytypecho'`
  和游离字符串，改为正式模块 docstring。

### 修复

- `Typecho.get_post` 实参顺序错误：`metaWeblog.getPost` 的签名是
  `(post_id, username, password)`，第一个参数不是 `blog_id`。原实现按
  `(blog_id, username, password, post_id)` 发送，取任何一篇文章都失败。
- `Typecho.del_post` 实参顺序错误：`blogger.deletePost` 的签名是
  `(blog_id, post_id, username, password, publish)`，原实现把 `post_id` 放在最后，
  服务端会把用户名当成文章 ID，删除始终失败。
- `PageDetail._head_info_str` 在 `tags` 为字符串时用 `','.join()` 把它拆成了单个字符
  （`python` → `p,y,t,h,o,n`），写回笔记头部的标签全是乱的；现在字符串原样保留，
  列表才做拼接。
- `PageDetail._read_ipynb` 在「整个 notebook 只有一个头部信息 cell」时，删除该 cell 后
  仍按下标取 cell 做模板，抛 `IndexError`；现在改为新建 markdown cell。
- `PageDetail` 读文件不再泄漏文件句柄（`open(...).read()` 改为 `with`）。
- `script/__version__.md`（原为 `0.5.7`）与 `pyproject.toml` 的版本号不一致，现已同步。

### 废弃

- 无。

## [0.5.8]

### 新增

- 无。

### 变更

- 破坏性变更：源码包名 / import 路径 / PyPI 发布名从 `noteblog` 改为 `funblog`，与 GitHub 仓库名保持一致（此前已完成 `noteblog` → `funblog` 的仓库改名）。
  - 迁移方法：将代码中的 `import noteblog` / `from noteblog...` 全部改为 `import funblog` / `from funblog...`。
  - `noteblog` 从未实际发布到 PyPI（已确认 404），因此不需要旧包转发版本，属于无兼容层的直接改名。
  - 相关背景：farfarfun/todo-list#299。
- `pyproject.toml` 补齐运行时依赖 `nbformat`、`nbconvert`（此前代码已在使用但未声明），并为全部依赖补上版本下限。
- README 补充组织介绍区块与 MIT 协议声明。
- `funblog/utils/brush/` 下的模块文件由 PascalCase 改为 snake_case（`Brush.py`→`brush.py`、`EmailClient.py`→`email_client.py`、`TempEmail.py`→`temp_email.py`）。

### 修复

- 修复日志（改用 `farlog`，去掉导入期副作用）、异常处理（`raise Exception` 改为领域相关的 `NotImplementedError`）、`print` 诊断输出、旧式 `typing.Optional/List/Dict` 标注等代码规范问题；删除与线上代码完全重复且未被引用的 `funblog/blog/typecho/core/` 死代码目录（详见 farfarfun/todo-list#360）。

### 废弃

- 无。
