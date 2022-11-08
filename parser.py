from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException


# TODO: убрать импорты и объединить в один


class Rezka:
    def __init__(self, search_request: str):
        self.search_request = search_request
        self.url = None
        self.name = None
        self.search_results = None
        self.info = None
        self.selected_vse = [0, 0, 0]

        try:
            webdriver.Chrome(desired_capabilities=cap, options=options)
        except WebDriverException:
            self.name = "Chromedriver is out of date"
            # TODO: придумать как уведомлять о том, что хромдрайвер устарел

    def search(self):
        driver = webdriver.Chrome()
        driver.get("https://hdrezka.ag/search/?do=search&subaction=search&q=" + self.search_request)
        results = driver.find_elements(By.CLASS_NAME, "b-content__inline_item")
        data = {"results": []}
        for result in results:
            text = result.text.split("\n")
            series = True if len(text) == 4 else False
            data["results"].append({
                "id": results.index(result),
                "type": text[0],
                "status": text[1] if series else "-",
                "name": text[2] if series else text[1],
                "info": text[3] if series else text[2],
                "link": result.get_attribute("data-url")
                })
        driver.quit()
        self.search_results = data
        return data

    def select_result(self, selected_id: int):
        for result in self.search_results["results"]:
            if result["id"] == selected_id:
                self.name = result["name"]
                self.url = result["link"]
                self.info = {}
                self.selected_vse = [0, 0, 0]
                break
        return self.name

    def get_voices(self):
        try:
            audio_tracks = {element.text: element.get_attribute("data-translator_id")
                            for element in self.driver.find_elements(By.CLASS_NAME, r'^b-translator__item')}
        except NoSuchElementException:
            audio_tracks = None
        return audio_tracks

    def select_voice(self, voice_id: int):
        for element in self.driver.find_elements(By.CLASS_NAME, r'^b-translator__item'):
            if element.get_attribute("data-translator_id") == voice_id:
                element.click()
                self.selected_vse[0] = voice_id
                return element.text
        return None

    def get_seasons(self):
        try:
            seasons = [element.text for element in self.driver.find_elements(By.CLASS_NAME, r'^b-simple_season__item')]
        except NoSuchElementException:
            seasons = None
        return seasons

    def select_season(self, season_id: int):
        for element in self.driver.find_elements(By.CLASS_NAME, r'^b-simple_season__item'):
            if element.get_attribute("data-tab_id") == season_id:
                element.click()
                self.selected_vse[1] = season_id
                return element.text
        return None

    def get_episodes(self):
        # TODO: Нужно ли добавлять self.driver.get(self.url) ?
        try:
            episodes = [element.get_attribute("data-episode_id")
                        for element in self.driver.find_elements(By.CLASS_NAME, r'^b-simple_episode__item')]
        except NoSuchElementException:
            episodes = None
        return episodes

    def select_episode(self, episode_id: int):
        for element in self.driver.find_elements(By.CLASS_NAME, r'^b-simple_episode__item'):
            if element.get_attribute("data-episode_id") == episode_id:
                element.click()
                self.selected_vse[2] = episode_id
                return element.text
        return None

    def information(self, url=None):
        url = self.url if not url else url
        driver = webdriver.Chrome()
        driver.get(url)
        try:
            original_title = driver.find_element(By.CLASS_NAME, 'b-post__origtitle').text
        except NoSuchElementException:
            original_title = driver.find_element(By.CLASS_NAME, 'b-post__title')
        try:
            other_parts = {element.text: element.get_attribute("data-url")
                           for element in driver.find_elements(By.CLASS_NAME, 'b-post__partcontent_item')}
        except NoSuchElementException:
            other_parts = None

        info = {
            "original_title": original_title,
            "rating_imdb": driver.find_element(By.CLASS_NAME, 'b-post__info_rates imdb').text,
            "rating_kp": driver.find_element(By.CLASS_NAME, 'b-post__info_rates kp').text,
            "rating_hdrezka": driver.find_element(By.CLASS_NAME, r'^rating-layer-num-').text,
            "description": driver.find_element(By.CLASS_NAME, 'b-post__description_text').text,
            "audio_tracks": self.get_voices(),
            "seasons": self.get_seasons(),
            "other_parts": other_parts,
        }

        driver.quit()
        self.info = info
        return info

    def get_links(self, url=None, search_filter="m3u", sub_filter=None):
        """
        Returns a list of links on successful search with the given filter.
        Arguments:
            search_filter - Content search filter from download logs
                            Set to "m3u" by default
            sub_filter - Search subfilter,
                         Set to "mp4" by default if search filter is "m3u" or "m3u8"
        """
        # TODO: rename search_filter to log_search_filter

        url = self.url if not url else url
        sub_filter = sub_filter if sub_filter or search_filter not in ['m3u', 'm3u8'] else "mp4"

        options = Options()
        options.headless = headless
        cap = DesiredCapabilities.CHROME
        cap["goog:loggingPrefs"] = {'performance': 'ALL'}
        driver = webdriver.Chrome(desired_capabilities=cap, options=options)

        driver.get(url)
        links = []
        for line in driver.get_log('performance'):
            line = str(line)
            i_begin = 0
            i_end = len(line)
            if search_filter in line:
                for i in range(line.find(sub_filter), len(line)):
                    if line[i] == '"':
                        i_end = i
                        break
                for i in range(line.find(sub_filter), 0, -1):
                    if line[i] == '"':
                        i_begin = i + 1
                        break
            # TODO: Раскопать json, проходя по логам не превращая их в строки, может получится.
            #  Если раскопали json, то переделать поиск не по всей строке а по значению ключа
                link = line[i_begin: i_end]
                links.append(link)
        driver.close()
        return links

    def __str__(self):
        return self.name
