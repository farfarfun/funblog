#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/04/30 01:15
# @Author  : niuliangtao
# @Site    : 
# @File    : TemMail.py
# @Software: PyCharm

import re
from time import sleep

import requests
from splinter.browser import Browser


class TemMail:
    def __init__(self):
        self.driver_name = 'chrome'
        self.executable_path = '/usr/local/bin/chromedriver'

        self.driver = Browser(driver_name=self.driver_name, executable_path=self.executable_path)
        self.driver.driver.set_window_size(800, 800)
        self.driver.visit('https://www.moakt.com')
        self.driver.find_by_name('random').click()
        while self.driver.url == 'https://www.moakt.com/zh/mail':
            return

    def getMailName(self):
        sleep(1)
        self.driver.execute_script('changeAddress();')
        sleep(1)
        mail_name = self.driver.find_by_id('email-address').text
        return mail_name

    def getEmail(self):

        while True:
            self.driver.find_by_text(u"刷新列表").click()
            temdata = self.driver.find_by_text(u"激活您的ProcessOn帐号")
            if len(temdata) == 0:
                sleep(2)
            else:
                em = self.driver.find_by_text(u"激活您的ProcessOn帐号").first
                url = em["href"] + '/content'
                self.getEmailDea(url)
                break

    def getEmailDea(self, emlurl):

        self.driver.visit(emlurl)
        temtext = self.driver.html
        url_verify = re.findall(r"https://www.processon.com/signup/verification/\w+", temtext)
        ss_mail = requests.Session()
        rsp_verify = ss_mail.get(url_verify[0])

        if rsp_verify.status_code == 200:
            self.driver.quit()
        else:
            print("failure：" + rsp_verify.status_code)
