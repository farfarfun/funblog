from notetool.tool.secret import read_secret

rpc_url = read_secret(cate1='blog', cate2='typecho', cate3='rpc_url')
username = read_secret(cate1='blog', cate2='typecho', cate3='username')
password = read_secret(cate1='blog', cate2='typecho', cate3='password')
