from noteblog.publish.core import BlogManage
from notetool.tool.secret import read_secret

# pip install  git+https://gitee.com/notechats/noteblog.git
# pip install  git+https://gitee.com/notechats/notetool.git

blog = BlogManage('/root/workspace/content/publish',
                  db_path='/root/workspace/content/blog.db')

rpc_url = read_secret(cate1='blog', cate2='typecho', cate3='rpc_url')
username = read_secret(cate1='blog', cate2='typecho', cate3='username')
password = read_secret(cate1='blog', cate2='typecho', cate3='password')
#blog.local_scan()
blog.publish_typecho(rpc_url=rpc_url, username=username, password=password)
