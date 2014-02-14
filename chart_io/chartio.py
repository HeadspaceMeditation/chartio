"""
   Copyright 2014 Ginger.io, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Used to generate PDF reports of Chart.io dashboards.

Note that PhantomJS is so fast that sleeping is required throughout the code.
"""
from time import sleep
from PIL import Image
from StringIO import StringIO
import base64
import logging
import sys

from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException


logger = logging.getLogger('ginger.sales')


class LoginFailedException(Exception):
    pass


class InvalidFilterException(Exception):
    pass


class ChartioDashboardRetriever(object):
    PHANTOMJS_PATH = '/usr/bin/phantomjs'
    LOGIN_URL = 'https://chartio.com/login'
    PROJECTS_URL = 'https://chartio.com/project/'
    LOGOUT_URL = 'https://chartio.com/logout/'
    TIMEOUT = 10

    def __init__(self, username, password, debug=False):
        self.username = username
        self.password = password
        self.debug = debug

        self.browser = self._configure_browser()
        self._login(username, password)

    def get_pdf_for_dashboard(self, dashboard_url, global_filter_values=None):
        try:
            self._load_dashboard(dashboard_url)
            merger = PdfFileMerger()
            if not global_filter_values:
                merger.append(self._get_screenshot_as_pdf())
            else:
                for filter_value in global_filter_values:
                    if not self._filter_dashboard(filter_value.strip()):
                        self.save_screenshot('failed_{}.pdf'.format(filter_value.replace(' ', '_')))
                        continue
                    merger.append(self._get_screenshot_as_pdf())
            if self.debug:
                merger.write('chartio_test.pdf')
            return self._convert_merger_to_pdf(merger)
        except WebDriverException:
            self.save_screenshot('exception_screenshot.pdf')
            raise

    def save_screenshot(self, filename='screenshot.pdf'):
        writer = PdfFileWriter()
        writer.addPage(self._get_screenshot_as_pdf().getPage(0))
        writer.write(file(filename, 'wb'))

    def close(self):
        self.browser.get(self.LOGOUT_URL)
        self.browser.close()

    def _configure_browser(self):
        if self.debug:
            browser = webdriver.Firefox()
            self.enter_key = Keys.RETURN
        else:
            # http://stackoverflow.com/a/20895651/444654
            try:
                browser = webdriver.PhantomJS(self.PHANTOMJS_PATH)
            except WebDriverException:
                browser = webdriver.PhantomJS(self.PHANTOMJS_PATH)
            self.enter_key = Keys.ENTER
            browser.set_window_size(1920, 1000)
        return browser

    def _login(self, username, password):
        self.browser.get(self.LOGIN_URL)
        email_ = self.browser.find_element_by_name('email')
        email_.send_keys(username)
        password_ = self.browser.find_element_by_name('password')
        password_.send_keys(self.password)
        password_.submit()
        if self.browser.current_url == self.LOGIN_URL:
            # Already signed in. Confirm signing out of other browser.
            assert 'Accounts already logged in' in self.browser.page_source
            button = self.browser.find_element_by_css_selector('button')
            button.click()
        if self.browser.current_url != self.PROJECTS_URL:
            raise LoginFailedException

    def _load_dashboard(self, dashboard_url):
        self.browser.get(dashboard_url)
        self._wait_for_charts_to_load()
        presentation_mode_button = self.browser.find_element_by_id('presentation-mode-toggle')
        presentation_mode_button.click()
        sleep(1)  # for Phantom
        self.filter_input = self.browser.find_element_by_css_selector('input')

    def _filter_dashboard(self, filter_value):
        self.filter_input.send_keys([Keys.BACK_SPACE, Keys.BACK_SPACE])
        sleep(1)
        self.filter_input.send_keys(filter_value)
        sleep(1)
        self.filter_input.send_keys(self.enter_key)
        self._wait_for_charts_to_load()
        if not self._text_in_title(filter_value):
            msg = 'No matches found for {}'.format(filter_value)
            if self.debug:
                print 'Error:', msg
            else:
                logger.error(msg)
            return False
        return True

    def _wait_for_charts_to_load(self):
        sleep(1)  # for PhantomJS
        try:
            WebDriverWait(self.browser, self.TIMEOUT).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, 'loading')))
        except TimeoutException as e:
            e.message = e.message + 'Timed out waiting for charts to load.'
            raise
        sleep(1)  # Prevent StaleElementReferenceException in _text_in_title

    def _text_in_title(self, text):
        tags = self.browser.find_elements_by_tag_name('tspan')
        if [t for t in tags if text in t.text]:
            return True
        print [t.text for t in tags]  # For debugging failures
        return False

    def _convert_merger_to_pdf(self, merger):
        buffer_ = StringIO()
        merger.write(buffer_)
        merged_pdf = buffer_.getvalue()
        buffer_.close()
        return merged_pdf

    def _get_screenshot_as_pdf(self):
        png = base64.decodestring(self.browser.get_screenshot_as_base64())
        im_png = Image.open(StringIO(png)).convert('RGB')  # RGBA cannot be converted to PDF
        buffer_ = StringIO()
        im_png.save(buffer_, format='PDF')
        pdf = PdfFileReader(buffer_)
        return pdf


if __name__ == '__main__':
    """
    For testing with Firefox at command line. Example:
        python chartio.py jeremy@ginger.io {password} {dashboard_url} "Filter Value 1,Filter Value 2"
    
    Uses FireFox and will write PDF to `chartio_test.pdf`
    
    Useful for debugging interactively:
      from IPython.core.debugger import Tracer
      Tracer()() # to break into ipdb
    """
    username, password, dashboard_url, filter_values_str = sys.argv[1:5]
    filter_values = filter_values_str.split(',')
    chartio = ChartioDashboardRetriever(username, password, debug=True)
    chartio.get_pdf_for_dashboard(dashboard_url, filter_values)
    chartio.close()
