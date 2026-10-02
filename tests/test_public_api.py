"""公开 API 的行为测试：Typecho XML-RPC 参数顺序、本地笔记解析与目录扫描。"""

from pathlib import Path
from xmlrpc.client import Binary, Fault, dumps

import nbformat
import pytest

from funblog.blog.typecho import Attachment, Category, Post, Typecho
from funblog.core.meta import PageDetail
from funblog.publish.core import get_all_file


def make_client() -> Typecho:
    """构造一个不发起网络连接的 Typecho 客户端。"""
    client = object.__new__(Typecho)
    client.rpc_url = "https://example.test/action/xmlrpc"
    client.username = "user"
    client.password = "secret"
    client.blog_id = 1
    return client


class RecordingMethod:
    """假 ServerProxy 的方法代理，记录完整方法名与实参。"""

    def __init__(self, name: str, calls: list):
        self._ServerProxy__name = name
        self._calls = calls

    def __getattr__(self, name):
        return RecordingMethod(f"{self._ServerProxy__name}.{name}", self._calls)

    def __call__(self, *args, **kwargs):
        self._calls.append((self._ServerProxy__name, args))
        return "ok"


class RecordingProxy:
    """记录调用参数的假 ServerProxy，用于校验 XML-RPC 实参顺序。"""

    def __init__(self):
        self.calls: list[tuple[str, tuple]] = []

    def __getattr__(self, name):
        return RecordingMethod(name, self.calls)


def test_try_rpc_prepends_auth_arguments():
    """try_rpc 必须按 (blog_id, username, password, ...) 的顺序补齐鉴权参数。"""
    client = make_client()
    proxy = RecordingProxy()
    client.s = proxy

    client.get_posts(5)

    assert proxy.calls == [("metaWeblog.getRecentPosts", (1, "user", "secret", 5))]


def test_get_post_puts_post_id_first():
    """metaWeblog.getPost 的签名是 (post_id, username, password)，不带 blog_id。"""
    client = make_client()
    proxy = RecordingProxy()
    client.s = proxy

    client.get_post(42)

    assert proxy.calls == [("metaWeblog.getPost", (42, "user", "secret"))]


def test_del_post_puts_post_id_before_credentials():
    """blogger.deletePost 的签名是 (blog_id, post_id, username, password, publish)。"""
    client = make_client()
    proxy = RecordingProxy()
    client.s = proxy

    client.del_post(42)

    assert proxy.calls == [("blogger.deletePost", (1, 42, "user", "secret", True))]


def test_get_page_puts_page_id_after_blog_id():
    """wp.getPage 的签名是 (blog_id, page_id, username, password)。"""
    client = make_client()
    proxy = RecordingProxy()
    client.s = proxy

    client.get_page(7)

    assert proxy.calls == [("wp.getPage", (1, 7, "user", "secret"))]


def test_edit_post_carries_post_id_in_content():
    """编辑文章走 metaWeblog.newPost + 内容里的 postId，Typecho 以此定位已有文章。"""
    client = make_client()
    proxy = RecordingProxy()
    client.s = proxy

    client.edit_post(Post(title="标题", description="正文"), 99, True)

    method, args = proxy.calls[0]
    assert method == "metaWeblog.newPost"
    assert args[:3] == (1, "user", "secret")
    assert args[3]["postId"] == 99
    assert args[3]["title"] == "标题"


def test_empty_rpc_result_is_normalized_to_none():
    """服务端返回空字符串时统一转成 None。"""
    client = make_client()

    def empty_rpc(*args, **kwargs):
        return ""

    assert client._try_rpc(empty_rpc) is None


def test_typecho_rpc_fault_is_not_silenced():
    """服务端报错必须抛出，不能被日志吞掉后返回 None。"""
    client = make_client()

    def failing_rpc(*args, **kwargs):
        raise Fault(403, "forbidden")

    with pytest.raises(Fault, match="forbidden"):
        client._try_rpc(failing_rpc)


def test_models_are_xmlrpc_serializable():
    """分类 / 文章 / 附件都要能被 XML-RPC 序列化，否则调用直接抛 TypeError。"""
    payload = dumps(
        (
            Category(name="分类", parent=0),
            Post(title="标题", description="正文", categories=["分类"]),
            Attachment(name="a.png", bytes=Binary(b"\x89PNG")),
        ),
        methodname="m",
    )

    assert "<name>categories</name>" in payload
    assert "<base64>" in payload


def test_head_info_str_keeps_tag_string_intact():
    """tags 是字符串时不能被逐字符 join 成 'p,y,t,h,o,n'。"""
    page = PageDetail(title="标题", tags="python,blog", page_uid="uid-1")

    text = page._head_info_str()

    assert "- tags: python,blog" in text
    assert "- title: 标题" in text
    assert "- uid: uid1" in text


def test_head_info_str_joins_tag_list():
    """tags 是列表时按逗号拼接。"""
    page = PageDetail(title="标题", tags=["python", "blog"], page_uid="uid-1")

    assert "- tags: python,blog" in page._head_info_str()


def test_head_info_parse_roundtrip():
    """头部元信息解析后应回填到实例属性。"""
    page = PageDetail()

    page._head_info_parse("- title: 标题\n- tags: a,b\n- uid: abc-def\n")

    assert page.title == "标题"
    assert page.tags == "a,b"
    assert page.page_uid == "abcdef"


def test_name_convent_strips_leading_order_digits():
    """文件名前导的排序数字与分隔符不进标题。"""
    assert PageDetail.name_convent("01-入门指南") == "入门指南"
    assert PageDetail.name_convent("入门指南") == "入门指南"


def test_read_ipynb_with_only_head_cell(tmp_path: Path):
    """整个 notebook 只有一个头部信息 cell 时不能越界崩溃。"""
    notebook = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_markdown_cell("- title: 仅头部\n- uid: abc\n")]
    )
    path = tmp_path / "note.ipynb"
    path.write_text(nbformat.writes(notebook), encoding="utf-8")

    page = PageDetail(path=str(path))
    content = page.init_page()

    assert content.strip() == ""
    # 头部信息被重新写回文件，文件仍然是合法 notebook
    assert nbformat.reads(path.read_text(encoding="utf-8"), as_version=4).cells


def test_read_md_uses_file_content(tmp_path: Path):
    """`.md` 文件直接读全文，标题取自文件名。"""
    path = tmp_path / "02-随笔.md"
    path.write_text("# 正文\n", encoding="utf-8")

    page = PageDetail(path=str(path))

    assert page.content == "# 正文\n"
    assert page.title == "随笔"


def test_get_all_file_builds_category_tree(tmp_path: Path):
    """目录变成分类，`.md`/`.ipynb` 变成文章，`.ipynb_checkpoints` 被跳过。"""
    (tmp_path / "分类A").mkdir()
    (tmp_path / "分类A" / "a.md").write_text("a", encoding="utf-8")
    (tmp_path / "分类A" / "skip.txt").write_text("x", encoding="utf-8")
    (tmp_path / ".ipynb_checkpoints").mkdir()
    (tmp_path / ".ipynb_checkpoints" / "b.md").write_text("b", encoding="utf-8")

    tree = get_all_file(str(tmp_path))

    assert [c.name for c in tree.categories] == ["分类A"]
    assert [Path(f).name for f in tree.categories[0].files] == ["a.md"]
