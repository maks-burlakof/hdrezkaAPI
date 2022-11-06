from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
# TODO: убрать импорты и объединить в один


class Rezka:
    def __init__(self, url, search_filter="m3u", sub_filter=None, headless=True):

        """
        url - link to content from hdrezka.ag
        search_filter - Content search filter from download logs
                        Set to "m3u" by default
        sub_filter - Search subfilter,
                     Set to "mp4" by default if search filter is "m3u" or "m3u8"
        headless - Chrome driver launch option,
                   Set to True by default
        """

        self.url = url
        self.search_filter = search_filter
        if not sub_filter:
            if search_filter in ['m3u', 'm3u8']:
                self.sub_filter = "mp4"
            else:
                self.sub_filter = search_filter
        else:
            self.sub_filter = sub_filter
        self.headless = headless

    def get_links(self):

        """
        Returns a list of links on successful search with the given filter (code 100).
        Returns error codes:
            201 - chromedriver is out of date.
            202 - no records found containing the current filter.
        """

        options = Options()
        options.headless = self.headless
        cap = DesiredCapabilities.CHROME
        cap["goog:loggingPrefs"] = {'performance': 'ALL'}
        try:
            driver = webdriver.Chrome(desired_capabilities=cap, options=options)
        except WebDriverException:
            return "Error: The chromedriver is outdated.", 201

        driver.get(self.url)
        links = []

        for line in driver.get_log('performance'):
            line = str(line)
            i_begin = 0
            i_end = len(line)
            if self.search_filter in line:
                for i in range(line.find(self.sub_filter), len(line)):
                    if line[i] == '"':
                        i_end = i
                        break
                for i in range(line.find(self.sub_filter), 0, -1):
                    if line[i] == '"':
                        i_begin = i + 1
                        break
            # TODO: Раскопать json, проходя по логам не превращая их в строки, может получится.
            #  Если раскопали json, то переделать поиск не по всей строке а по значению ключа
                link = line[i_begin: i_end]
                links.append(link)
        driver.close()

        if not links:
            return f'Error: No links containing a "{self.search_filter}" filter were found.', 202
        return links, 100
