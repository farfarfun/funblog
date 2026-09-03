# 更新日志

本文件记录 `funblog` 的版本变更，按版本倒序排列。

## [0.5.8]（当前版本）

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
