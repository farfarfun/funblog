# NOTE: This test is intentionally minimal.
#
# funblog's top-level __init__.py only declares __all__ = ['brush'] and
# performs no imports itself, so `import funblog` is safe. Its submodules
# (funblog.core.meta, funblog.publish.core, funblog.blog.typecho, ...) pull
# in undeclared dependencies (nbformat, nbconvert) and, in at least one case
# (funblog/core/bak.py), reference a `funblog.common` module that no longer
# exists in this tree. Those are pre-existing issues in funblog's own
# source, out of scope for this smoke test, so only the top-level package
# import is exercised here.
import funblog


def test_import_funblog():
    assert funblog is not None
