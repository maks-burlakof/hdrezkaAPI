from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException


class Rezka:
    def __init__(self, search_request: str, headless: bool = True):
        self.search_request = search_request
        self.url = None
        self.name = None
        self.search_results = None
        self.info = None
        self.selected_vse = [0, 0, 0]

        self.cap = DesiredCapabilities.CHROME
        self.cap["pageLoadStrategy"] = "eager"
        self.options = Options()
        self.options.headless = headless
        self.options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})

    def search(self):
        driver = webdriver.Chrome(options=self.options, desired_capabilities=self.cap)
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

    def select_result(self, result_id: int):
        for result in self.search_results["results"]:
            if result["id"] == result_id:
                self.name = result["name"]
                self.url = result["link"]
                self.info = {}
                self.selected_vse = [0, 0, 0]
                break
        return self.name

    def get_voices(self, driver: WebDriver):
        try:
            audio_tracks = {element.text: int(element.get_attribute("data-translator_id"))
                            for element in driver.find_elements(By.CLASS_NAME, 'b-translator__item')}
        except NoSuchElementException:
            audio_tracks = None
        return audio_tracks

    def select_voice(self, voice_id: int, driver: WebDriver):
        for element in driver.find_elements(By.CLASS_NAME, 'b-translator__item'):
            if element.get_attribute("data-translator_id") == voice_id:
                element.click()
                self.selected_vse[0] = voice_id
                return element.text
        return None

    def get_seasons(self, driver: WebDriver):
        try:
            seasons = [int(element.get_attribute("data-tab_id"))
                       for element in driver.find_elements(By.CLASS_NAME, 'b-simple_season__item')]
        except NoSuchElementException:
            seasons = None
        return seasons

    def select_season(self, season_id: int, driver: WebDriver):
        for element in driver.find_elements(By.CLASS_NAME, 'b-simple_season__item'):
            if element.get_attribute("data-tab_id") == season_id:
                element.click()
                self.selected_vse[1] = season_id
                return element.text
        return None

    def get_episodes(self, driver: WebDriver):
        try:
            episodes = [int(element.get_attribute("data-episode_id"))
                        for element in driver.find_elements(By.CLASS_NAME, 'b-simple_episode__item')]
        except NoSuchElementException:
            episodes = None
        return episodes

    def select_episode(self, episode_id: int, driver: WebDriver):
        for element in driver.find_elements(By.CLASS_NAME, 'b-simple_episode__item'):
            if element.get_attribute("data-episode_id") == episode_id:
                element.click()
                self.selected_vse[2] = episode_id
                return element.text
        return None

    def get_seasons_episodes(self, driver: WebDriver):
        seasons_episodes = {}
        seasons = self.get_seasons(driver)
        if seasons:
            for season in seasons:
                season_element = driver.find_element(By.ID, "simple-episodes-list-" + str(season))
                episodes = max([int(episode_element.get_attribute("data-episode_id"))
                                for episode_element in season_element.find_elements(By.CLASS_NAME,
                                                                                    "b-simple_episode__item")])
                seasons_episodes.update({season: episodes})
        else:
            episodes = self.get_episodes(driver)
            if episodes:
                seasons_episodes.update({1: max(episodes)})
            else:
                seasons_episodes = {}
        return seasons_episodes

    def information(self, url=None):
        url = self.url if not url else url
        driver = webdriver.Chrome(options=self.options, desired_capabilities=self.cap)
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
            "info": driver.find_element(By.CLASS_NAME, "b-post__info").text,
            "description": driver.find_element(By.CLASS_NAME, 'b-post__description_text').text,
            "audio_tracks": self.get_voices(driver),
            "seasons_episodes": self.get_seasons_episodes(driver),
            "other_parts": other_parts,
        }

        driver.quit()
        self.info = info
        return info

    def get_links(self, url=None, search_filter="m3u", sub_filter=None):
        url = self.url if not url else url
        if not sub_filter and search_filter in ['m3u', 'm3u8']:
            sub_filter = "mp4"

        cap = DesiredCapabilities.CHROME
        cap["goog:loggingPrefs"] = {'performance': 'ALL'}
        cap["pageLoadStrategy"] = "normal"
        driver = webdriver.Chrome(desired_capabilities=cap, options=self.options)

        driver.get(url)
        links = []
        for line in driver.get_log('performance'):
            line = str(line)
            i_begin = 0
            i_end = len(line)
            if search_filter in line:
                if not sub_filter:
                    for i in range(line.find(search_filter), len(line)):
                        if line[i] == '"':
                            i_end = i
                            break
                else:
                    i_end = line.find(sub_filter) + len(sub_filter)
                for i in range(line.find(search_filter), 0, -1):
                    if line[i] == '"':
                        i_begin = i + 1
                        break
                link = line[i_begin: i_end]
                links.append(link)
        driver.quit()
        return links

    def __str__(self):
        return self.name
