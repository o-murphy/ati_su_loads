import json
import logging
import pickle
from time import sleep

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver
from seleniumwire.request import Request, Response
from modules.config import CONFIG


# setup scraper logger
scraper_log = logging.getLogger("scraper_log")
scraper_log.setLevel(CONFIG['logger']['level'])

# web driver options
OPTIONS = webdriver.ChromeOptions()
for opt in CONFIG['scrapper']['driver_options']:
    OPTIONS.add_argument(opt)

# chrome capabilities
CAPS = DesiredCapabilities.CHROME
CAPS['goog:loggingPrefs'] = {'performance': 'ALL'}

# seleniumwire proxy request scopes
SCOPES = [
    '.*ati.su/webapi/public/v1.0/loads/search',
    '.*ati.su/webapi/v1.0/loads/search',
]

# seleniumwire options
SELENIUMWIRE_OPTIONS = {"disable_encoding": True}

# default timeouts
GET_TIMEOUT = 12
UPDATE_TIMEOUT = 2
SCRAP_TIMEOUT = 10

with open(CONFIG['scrapper']['cookies_path'], "rb") as coockie:
    COOKIE = pickle.load(coockie)


class NotifyCallBack:
    def __init__(self, sender_id: int, callback: callable):
        """
        :param sender_id:
        :param callback:
        """
        self.sender_id = sender_id
        self.callback_func = callback

    def callback(self, data: dict):
        """
        runs installed callback
        :param data:
        :return:
        """
        self.callback_func(self.sender_id, data)


class Scraper:
    _callback_data: NotifyCallBack = None

    def __init__(self):
        self.driver = webdriver.Chrome(
            options=OPTIONS,
            desired_capabilities=CAPS,
            seleniumwire_options=SELENIUMWIRE_OPTIONS,
        )
        self.driver.scopes = SCOPES
        self.driver.set_page_load_timeout(GET_TIMEOUT)
        self.driver.response_interceptor = self.resp_intercept
        self.last_load_id = None

    def update_pretty_loads(self):
        """
        updates pretty loads list
        :return:
        """
        self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.RETURN)
        sleep(UPDATE_TIMEOUT)
        scraper_log.info('loads update')

    def get(self, url: str):
        try:
            scraper_log.info(f'driver get on {url}')
            self.driver.get(url)
        except TimeoutException as err:
            scraper_log.info(f'stop loading by timeout, skip errors')
        except WebDriverException as err:
            scraper_log.info(err)
            raise RuntimeError(err)

    def stop(self):
        scraper_log.info('Driver stopping')
        self.driver.close()
        self.driver.quit()

    def load_cookie(self):
        for cookie in COOKIE:
            self.driver.add_cookie(cookie)

    def setup(self, url: str) -> bool:
        """
        setting up the main web page
        :param url:
        :return:
        """
        try:
            self.get(url)
            self.load_cookie()
            scraper_log.info('Cookie loaded')
            self.get(url)
            scraper_log.info('Page loading stopped by timeout')
        except RuntimeError as err:
            scraper_log.info('WebDriverException occurred')
            scraper_log.error(err)
            return False

        scraper_log.info('Data loaded')

        return True

    @staticmethod
    def _xhr2json(body: [bytes, str]) -> dict:
        """
        converts xhr data to dict
        :param body:
        :return:
        """
        body_decoded = body.decode('utf-8')  # decode string to utf-8
        return json.loads(body_decoded)

    def set_callback(self, callback: NotifyCallBack):
        self._callback_data = callback

    def resp_intercept(self, request: Request, response: Response) -> None:
        if request:
            scraper_log.info(f'request {request.id} {request.url}')
        if response:
            scraper_log.info(f"response {request.id} {request.url} {request.response.status_code}")
            if response.status_code == 200 and self._callback_data is not None:
                scraper_log.info(f'response ok {request.response.status_code}')
                body = request.response.body  # binary body
                data = self._xhr2json(body)
                filtered_data = list(filter(lambda x: 'priority' not in x, data['loads']))
                load = filtered_data[0]
                first_id = load['id']  # get first load id in the last search response
                if first_id == self.last_load_id:  # check if first load in list updated
                    scraper_log.info('no new loads')
                    return  # if load id the same return None
                scraper_log.info('new load found')
                self.last_load_id = first_id  # if load id new -> update last_load_id
                self._callback_data.callback(load)
            else:
                if response.status_code != 200:
                    scraper_log.warning(f'response error {request.response.status_code}')
                else:
                    scraper_log.warning(f'callback is not installed, stop scrapper and end valid url!')
        else:
            scraper_log.info('no updates found')

    def scrap(self):
        scraper_log.info('scrapping ...')
        self.update_pretty_loads()
        sleep(SCRAP_TIMEOUT)  # sleep before next scraping


if __name__ == '__main__':
    # example, run directly

    def req_intercept(request: Request):
        if request:
            print('request', request.id, request.url)


    def resp_intercept(request: Request, response: Response):
        if request:
            print('request', request.id, request.url)
        if response:
            body = response.body
            body_decoded = body.decode('utf-8')
            print(body_decoded)


    parser = Scraper()
    parser.driver.request_interceptor = req_intercept
    parser.driver.response_interceptor = resp_intercept
    parser.setup(
        "https://loads.ati.su/#?filter=%7B%22exactFromGeos%22:true,%22fromList%22:%7B%22id%22:%22ee634ef8-e210-e311-b4ec-00259038ec34%22,%22name%22:%22%D0%A6%D0%B5%D0%BD%D1%82%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9%20%D1%84%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9%20%D0%BE%D0%BA%D1%80%D1%83%D0%B3%22,%22type%22:0%7D,%22exactToGeos%22:true,%22toList%22:%7B%22id%22:%2279644ef8-e210-e311-b4ec-00259038ec34%22,%22name%22:%22%D0%AE%D0%B6%D0%BD%D1%8B%D0%B9%20%D1%84%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9%20%D0%BE%D0%BA%D1%80%D1%83%D0%B3%22,%22type%22:0%7D,%22firmListsExclusiveMode%22:false,%22dateFrom%22:%222022-10-24%22,%22dateOption%22:%22manual%22,%22extraParams%22:1,%22rate%22:1,%22rateType%22:3,%22withAuction%22:false%7D")

    while True:
        parser.update_pretty_loads()
        sleep(SCRAP_TIMEOUT)
