from noteblog.common.core import BlogManage
from notetool.tool.secret import read_secret

blog = BlogManage('/root/workspace/content/publish',
                  db_path='/root/workspace/content/publish/blog.db')

rpc_url = read_secret(cate1='blog', cate2='typecho', cate3='rpc_url')
username = read_secret(cate1='blog', cate2='typecho', cate3='username')
password = read_secret(cate1='blog', cate2='typecho', cate3='password')

blog.publish_typecho(rpc_url=rpc_url, username=username, password=password)
