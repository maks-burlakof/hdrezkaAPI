from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


def get_log(url, headless=True, filter=None):
    
    """
    Returns log on successful search with the given filter (code 100).
    Returns error codes:
        201 - chromedriver is out of date.
        202 - no records found containing the current filter.
    """
    
    options = Options()
    # options.add_experimental_option('w3c', False) ### added this line
    options.headless = headless
    cap = DesiredCapabilities.CHROME
    # cap['loggingPrefs'] = {'performance': 'ALL'}
    cap["goog:loggingPrefs"] = {'performance': 'ALL'}
    try:
        driver = webdriver.Chrome(desired_capabilities=cap, options=options)
    except WebDriverException:
        return "Ошибка: chromedriver устарел.", 201
    driver.get(url)
    
    if filter:
        log = [item for item in driver.get_log('performance') if filter in str(item)]
        if not log:
            return f'Ошибка: Записей, содержащих "{filter}" не найдено', 202
    else:
        log = driver.get_log('performance')
    driver.close()

    with open("log.txt", "w") as f:
        for line in log:
            f.write(str(line) + '\n')
    
    return str(log), 100


def log_processing(text):
    
    """Returns a list with .m3u8 links and .mp4 links."""
    
    links_m3u8 = []
    links_mp4 = []
    while "m3u8" in text:
        a = 0
        b = text.find("m3u8")
        while b - text.find("http") > 0 and "http" in text:
            a = text.find("http")
            text = text[a+4:]
        b = text.find("m3u8") + 4
        links_m3u8.append("http"+text[:b])
        if "mp4" in text[:b]:
            links_mp4.append("http"+text[:text.find(".mp4")+4])
        else:
            links_mp4.append("None")
        text = text[b+4:]
    return links_m3u8, links_mp4


def get_links(url, headless=True, filter=None, sub_filter=None):
    """
    Returns list of links on successful search with the given filter (code 100).
    Returns error codes:
        201 - chromedriver is out of date.
        202 - no records found containing the current filter.
    """

    options = Options()
    # options.add_experimental_option('w3c', False) ### added this line
    options.headless = headless
    cap = DesiredCapabilities.CHROME
    # cap['loggingPrefs'] = {'performance': 'ALL'}
    cap["goog:loggingPrefs"] = {'performance': 'ALL'}
    try:
        driver = webdriver.Chrome(desired_capabilities=cap, options=options)
    except WebDriverException:
        return "Ошибка: chromedriver устарел.", 201
    driver.get(url)

    links = []
    if filter:
        for item in driver.get_log('performance'):
            line = str(item)
            i_begin = 0
            i_end = len(line)
            if filter in line:
                for i in range(line.find("m3u"), len(line)):
                    if line[i] == '"':
                        i_end = i
                        break
                for i in range(line.find("m3u"), 0, -1):
                    if line[i] == '"':
                        i_begin = i
                        break
                link = line[i_begin+1:i_end]
                links.append(link)

        if not links:
            return f'Ошибка: Ссылок, содержащих "{filter}" не найдено', 202
    else:
        log = driver.get_log('performance')
    driver.close()

    with open("links.txt", "w") as f:
        for line in links:
            f.write(str(line) + '\n')

    return str(links), 100


get_links("http://kinopub.me/series/drama/7769-luchshe-zvonite-solu-2015.html#t:1-s:1-e:7",
        headless=False, filter="m3u")
