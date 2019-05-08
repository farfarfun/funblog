#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/05/05 15:44
# @Author  : niuliangtao
# @Site    : 
# @File    : EmailClient.py
# @Software: PyCharm

import datetime
# encoding: utf-8
import json
import random
import re
import string
import time
from time import sleep
from urllib.parse import urlencode

import requests
from tqdm import trange

__all__ = ["EmailClient", "EmailDataObject"]


class EmailDataObject(object):
    """邮件对象

    Attributes:
        subject (str): 邮件主题
        sendtime (datetime.datetime): 发送时间
        to_name (str): 发送者
        to_addr (str): 发送者地址
        from_name (str): 接收者
        from_addr (str): 接收者地址
        content (str): 邮件内容
        isread (bool): False未读
    """

    def __init__(self, obj, client=None):
        self.obj = obj
        self.subject = obj["SUBJECT"]
        self.sendtime = self.strptime(obj["SENDTIME"])
        self.to_name, self.to_addr = self.email_name(obj["TO"])
        self.from_name, self.from_addr = self.email_name(obj["FROM"])
        self.isread = obj["ISREAD"] != 0
        self._id = obj["MID"]
        self._content = obj.get("CONTENT") or obj.get("DATA")
        self._client = client

    @property
    def content(self):
        if not self._content and self._client:
            self.obj["CONTENT"] = self._content = \
                self._client.req_api("mailinfo", dict(f=self._id))[1][0]["DATA"][0]
        return self._content

    def email_name(self, name):
        match = re.search("^(.*)<(.+)>$", name)
        name, addr = match.group(1), match.group(2)
        return name or addr, addr

    def strptime(self, string):
        return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return "%(subject)s - %(from_name)s<%(from_addr)s> %(sendtime)s %(content)s" % dict(
            subject=self.subject,
            from_name=self.from_name,
            from_addr=self.from_addr,
            sendtime=self.sendtime,
            content=self.content
        )

    def __repr__(self):
        return "<%(classname)s %(subject)s from %(address)s>" % dict(
            classname=self.__module__ + "." + self.__class__.__name__,
            subject=self.subject,
            address=self.from_addr
        )


class BaseEmailClient(object):
    def __init__(self, name="", prefix="", suffix="chacuo.net"):
        self.prefix = prefix
        self.name = self.prefix + (name or self.random_name)
        self.suffix = suffix
        self.address = self.name + "@" + self.suffix

    def get_email_list(self):
        """
        获取邮件列表
        :return:
        """
        pass

    def check_received_email(self) -> bool:
        return False

    def wait_until_received_email(self, max_timeout=20) -> bool:
        """
        等待，直到接收到邮件
        :param max_timeout:最大超时时间 
        :return: 
        """
        progress = trange(max_timeout, desc="等待接收邮件")
        try:
            for _ in progress:
                if self.check_received_email():
                    return True
                sleep(1)
        finally:
            progress.close()
        return False

    @property
    def random_name(self):
        return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(11))

    def __str__(self):
        return self.address

    def __repr__(self):
        return "<%(classname)s %(address)s>" % dict(
            classname=self.__module__ + "." + self.__class__.__name__,
            address=self.address)


class EmailClient(BaseEmailClient):
    """基于24mail.chacuo.net的一个邮件接收类

    Args:
        name (:obj:`str`, optional): 邮箱名,默认值是一个11位的随机字符串
        prefix (:obj:`str`, optional): 邮箱名前缀,默认值空串
        suffix (:obj:`str`, optional): 邮箱域名,默认chacuo.net
            请填写24mail.chacuo.net支持的域名,暂不支持自己cname解析的域名
        session (:obj:`requests.Session`, optional): 会话对象,默认新建一个会话对象
    """

    base_url = "http://24mail.chacuo.net/"

    def __init__(self, name="", prefix="", suffix="chacuo.net", session=None):
        BaseEmailClient.__init__(self, name=name, prefix=prefix, suffix=suffix)
        self.session = session or requests.session()
        self.session.get(self.base_url)
        # 可能发生设置的name没有生效的情况 待处理
        self.req_api("set", dict(d=self.suffix))

    def check_received_email(self) -> bool:
        return len(self.get_email_list()) > 0

    def get_email_list(self):
        """接收邮件

        Returns:
            :obj:`list` of :obj:`EmailDataObject`: 邮件列表
        """
        data = self.req_api()
        return list(map(lambda o: EmailDataObject(o, self), data.get("list")))

    def req_api(self, type="refresh", arg=None):
        resp = self.session.post(self.base_url, dict(
            data=self.name,
            type=type,
            arg=urlencode(arg or dict()).replace("&", "_")
        ))
        return resp.json().get("data").pop()


class TempEmail(BaseEmailClient):
    """临时邮箱
    使用http://24mail.chacuo.net/10分钟邮箱,
    监听并返回收到的邮件内容,用以接受验证码
    """

    def __init__(self, name="", prefix="", suffix="chacuo.net", session=None):
        BaseEmailClient.__init__(self, name=name, prefix=prefix, suffix=suffix)
        self.headers = {
            'Pragma': 'no-cache',
            'Origin': 'http://24mail.chacuo.net',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'http://24mail.chacuo.net/',
        }
        # 使用会话先获取邮箱id
        self.session = session or requests.Session()
        self.mid = ''

    def check_received_email(self) -> bool:
        # 发送刷新检查是否有邮件并得到邮件id
        data = {
            'data': self.name,
            'type': 'refresh',
            'arg': ''
        }
        time.sleep(3)
        r = self.session.post('http://24mail.chacuo.net/', data=data)
        r_json = json.loads(r.text)
        try:
            mid = r_json['data'][0]['list'][0]['MID']
            self.mid = mid
        except IndexError:
            return False

        return True

    def get_email_list(self):

        # 获取邮件内容
        data2 = {
            'data': self.name,
            'type': 'mailinfo',
            'arg': 'f=' + str(self.mid)
        }
        r2 = self.session.post('http://24mail.chacuo.net/', data=data2)
        r2_json = json.loads(r2.text)

        email = EmailDataObject(r2_json['data'][0][1][0])

        # return list(map(lambda o: EmailDataObject(o, self), data.get("list")))
        return [email]


def main1():
    print("test1 begin")
    client = EmailClient(name="rqunhc98372")

    print(client.name)
    print(client.address)

    print("test1 over")


def main2():
    print("test2 begin")
    temp_email = TempEmail(name="bwngzo63428")
    print(temp_email.address)

    print(temp_email.check_received_email())
    print(temp_email.get_email_list())

    print("test2 over")


if __name__ == '__main__':
    main1()

    print()
    print()

    # main2()
