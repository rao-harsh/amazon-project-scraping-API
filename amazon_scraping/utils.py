from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import unquote, urlsplit
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO,
                    filename="./amazon_product_scraping.log", filemode="w")
logger = logging.getLogger()


def extract_url(raw_url):
    unquoted_url = unquote(raw_url)
    url_parts = urlsplit(unquoted_url)
    url = f"{url_parts.scheme}://{url_parts.netloc}{url_parts.path}"
    return url


def wait_for_elements(driver, xpath, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))


def safe_extract(element, xpath, attribute="text"):
    try:
        extracted_element = wait_for_elements(element, xpath)[0]
        if attribute == "text":
            return extracted_element.text
        elif attribute == "aria-label":
            return extracted_element.get_attribute("aria-label")
        elif attribute == "href":
            return extracted_element.get_attribute("href")
    except NoSuchElementException:
        return None


def fetch_data(search_query=""):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.amazon.in")
    elem = driver.find_element(By.XPATH, "//input[@id='twotabsearchtextbox']")
    elem.clear()
    elem.send_keys(search_query)
    elem.send_keys(Keys.ENTER)
    time.sleep(10)
    elements = wait_for_elements(
        driver, "//div[@data-component-type='s-search-result']")
    products = []
    elements = elements[0:7]
    for element in elements:
        product = {}
        try:
            price = safe_extract(element, ".//span[@data-a-size='xl']")
            name = safe_extract(
                element, ".//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']")
            rating = safe_extract(
                element, ".//div[@class='a-row a-size-small']/span[1]", attribute="aria-label")
            raw_url = safe_extract(
                element, ".//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']", attribute="href")
            url = extract_url(raw_url)
            product['price'] = price
            product['name'] = name
            product['rating'] = rating
            product['url'] = url
            products.append(product)
        except Exception as e:
            logger.error("Error while extracting product details: %s", str(e))

    driver.quit()
    return products


if __name__ == '__main__':
    fetched_data = fetch_data("samsung 23 inch monitor")
    for product in fetched_data:
        logger.info("Product Name: %s", product.get('name'))
        logger.info("Price: %s", product.get('price'))
        logger.info("Rating: %s", product.get('rating'))
        logger.info("URL: %s", product.get('url'))
