import random
import re
from time import sleep

from noteblog.brush.EmailClient import EmailClient
from splinter.browser import Browser
from tqdm import trange


def local_debug(msg):
    print(str(msg))


def get_random_str():
    random_str = str(random.randint(1000000, 9999999))
    return random_str


class ProcessOn:
    def __init__(self, web_url):
        try:
            self.email = EmailClient()
            self.driver_name = 'chrome'
            self.executable_path = '/usr/local/bin/chromedriver'

            self.driver = Browser(driver_name=self.driver_name, executable_path=self.executable_path)
            self.driver.driver.set_window_size(800, 800)
            self.driver.visit(web_url)
            self.driver.cookies.delete("processon_userKey")
            self.driver.find_by_text(u"注 册").first.click()
            sleep(1)
            if self.driver.url == 'https://tushare.pro/register':
                return

        except Exception as error:
            print(error)
            self.driver.quit()

    def signup(self):
        try:
            self.driver.fill("account", self.email.address)
            self.driver.fill("password", get_random_str())

            progress = trange(600, desc="等待填写验证码")
            for _ in progress:
                if self.driver.is_text_not_present(u'秒', 1):
                    break
                sleep(1)
            progress.close()
        except Exception as error:
            print(error)
            self.driver.quit()

    def getSecurityCode(self):
        try:
            self.email.wait_until_received_email(max_timeout=60)
            info = self.email.get_email_list()[0].content

            pat = "验证码([0-9]{6})"
            m = re.search(pat, info)

            return m.group(1)
        except Exception as error:
            print(error)
            return "000000"

    def input_code(self):
        try:
            code = self.getSecurityCode()
            self.driver.fill("verify_code", code)
            self.driver.find_by_id("register-btn").first.click()

        except Exception as error:
            print(error)

    def check_success(self):

        progress = trange(600, desc="等待完成注册")

        for _ in progress:
            if self.driver.is_text_present(u"没有账号？"):
                break
            sleep(1)

        progress.close()

    def clear(self):
        self.driver.cookies.delete()
        self.driver.quit()


def runlop(on_url):
    process = ProcessOn(on_url)

    process.signup()

    process.input_code()

    process.check_success()

    process.clear()
    sleep(1)
    print("\r【OK】")


if __name__ == '__main__':
    pass

    url = "https://tushare.pro/register?reg=233807"
    try:
        for i in range(0, 100):
            runlop(url)
    except Exception as e:
        print(e)

    print("================end================")
