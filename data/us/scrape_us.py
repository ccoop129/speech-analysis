
import csv
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

def scrape_page(url):
    """
    This function takes in a URL and returns the title, date, and content of the article.
    """
    # hit the URL and get the content and give it to BeautifulSoup
    response = requests.get(url)
    response.encoding = response.apparent_encoding  # fix mojibake from mis-detected encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    # use CSS selector to extract title
    title = soup.select_one(".news_header_title")
    # use CSS selector to extract date
    article_date = soup.select_one(".xltime")

    # use CSS selector to extract content
    content = soup.select_one(".content_text")

    # normalize and guard missing elements
    if title is not None:
        title_text = title.get_text(strip=True)
        title_text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', title_text)
    else:
        title_text = ''

    if article_date is not None:
        date_text = article_date.get_text(strip=True)
    else:
        date_text = ''

    if content is not None:
        content_text = content.get_text(separator=' ', strip=True)
    else:
        content_text = ''

    # return the extracted data
    return title_text, date_text, content_text

# get the index page
index_url = "https://www.fmprc.gov.cn/eng/xw/zyjh/"
records = []

# helper to process a single index page and collect article records
def process_index_page(page_url):
    response = requests.get(page_url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    article_links = soup.select(".news_list a")
    print(f"Found {len(article_links)} article links on {page_url}")
    count = 0
    for link in article_links:
        href = link.get("href")
        if not href:
            continue
        article_url = urljoin(page_url, href)
        title, date, content = scrape_page(article_url)
        print("Title:", title)
        records.append({"title": title, "date": date, "content": content})
        count += 1

    return count

# start from index_1 which mirrors the base index page
# then iterate numeric index pages: index_1.html, index_2.html, ...
index_num = 1
while True:
    page_url = f"{index_url}index_{index_num}.html"
    print("\nIndex page URL:", page_url)

    resp = requests.get(page_url)
    status = resp.status_code

    # stop when the page is not available/success
    if status != 200:
        break

    # collect articles from this index page; stop if none found
    found = process_index_page(page_url)
    if found == 0:
        print("No articles found on this index page — stopping.")
        break

    # move to next page
    index_num += 1

# write collected records to CSV
with open("china_speeches.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "date", "content"])
    writer.writeheader()
    writer.writerows(records)
