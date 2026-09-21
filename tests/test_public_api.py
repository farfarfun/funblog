from pathlib import Path

import pytest

from funblog.utils.blog2 import BlogConversionError, MetaWeblog, to_html
from funblog.utils.pyblog import BlogError


def test_to_html_rejects_unknown_extension(tmp_path: Path):
    source = tmp_path / "note.txt"
    source.write_text("text", encoding="utf-8")

    with pytest.raises(BlogConversionError):
        to_html(str(source), str(tmp_path / "note.html"))


def test_blog_error_repr_is_text_only():
    assert repr(BlogError("bad credentials")) == "bad credentials"


def test_metaweblog_repr_does_not_expose_password():
    blog = object.__new__(MetaWeblog)
    blog.serviceUrl, blog.usr, blog.passwd = "https://example.test", "user", "secret"

    assert "secret" not in repr(blog)
