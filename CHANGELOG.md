# Changelog

## Unreleased

### Breaking

- Renamed the source package / import name / PyPI distribution name from
  `noteblog` to `funblog` to match the GitHub repository name (already
  renamed from `noteblog` to `funblog` previously). Update any code using
  `import noteblog` / `from noteblog...` to `import funblog` / `from
  funblog...`.
  - `noteblog` was never actually published to PyPI (confirmed 404), so
    there is no old-package forwarding release needed — this is a clean
    rename with no compatibility shim.
  - Part of farfarfun/todo-list#299.
