import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://quotes.toscrape.com"

def get_soup(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "quote"))
    )
    page = driver.page_source
    return BeautifulSoup(page, "html.parser")


def get_quotes(quote_blocks):
    storage = []

    for block in quote_blocks:
        quote_data = {}
        tag_storage = []

        quote = block.find("span", class_="text")
        author = block.find("small", class_="author")
        tags = block.find_all("a", class_="tag")

        quote_data["author"] = author.text
        quote_data["quote"] = quote.text

        for item in tags:
            tag_storage.append(item.text)

        quote_data["tags"] = tag_storage
        storage.append(quote_data)

    return storage


def get_next_page_url(soup):
    next_button = soup.find("li", class_="next")
    if next_button:
        href = next_button.find("a")["href"]
        return BASE_URL + href
    return None


def scrape_all_quotes():
    driver = webdriver.Chrome()
    all_quotes = []

    try:
        current_url = f"{BASE_URL}/js/"

        while current_url:
            soup = get_soup(driver, current_url)
            quote_blocks = soup.find_all("div", class_="quote")

            page_quotes = get_quotes(quote_blocks)
            all_quotes.extend(page_quotes)

            current_url = get_next_page_url(soup)

    finally:
        driver.quit()

    return all_quotes


quotes_data = scrape_all_quotes()

with open("quotes.json", "w", encoding="utf-8") as file:
    json.dump(quotes_data, file, indent=4, ensure_ascii=False)

print(f"Scraped {len(quotes_data)} quotes and saved to quotes.json")
