import csv
import sys
from bs4 import BeautifulSoup
from selenium import webdriver

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

options = webdriver.ChromeOptions()
options.headless = True
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
header = ['Title', 'Price', 'Raiting', 'URL', 'Image_URL']

url = 'https://www.amazon.com/'
def search(item, page):
    new_url = 'https://www.amazon.com/s?k=' + item + '&ref=nb_sb_noss&page=' + str(page)
    driver.get(new_url)

# The condition for entering the search word
if (len(sys.argv) == 1): 
    driver.get(url)
else:
    result = sys.argv[1]
    search(result, 1)

filename = (str(sys.argv[1]) + '.csv')
with open(filename, 'w') as f:
    writer = csv.DictWriter(f, fieldnames = header)
    writer.writeheader()

def find_info(item):
    # Title of an item
    a_tag = item.h2.a
    desc = a_tag.text.strip()
    # URL to an item
    url = a_tag['href']
    final_url = 'https://amazon.com' + url
    # Price
    try:
        price = item.find('span', 'a-price')
        final_price = price.find('span','a-offscreen').text
    except AttributeError:
        return
    # Image URL
    image = item.find('img')
    final_image = image['src']
    # Stars of item
    try:
        stars = item.find('div', 'a-row a-size-small')
        star = stars.find('span')
        final_raiting = star['aria-label']
    except AttributeError:
        final_raiting = 'No raiting'
    # Returning the result
    result = (desc, final_price, final_raiting, final_url, final_image)
    with open(filename, 'a') as f:
        write = csv.writer(f)
        write.writerow(result)

soup = BeautifulSoup(driver.page_source, 'html.parser')
results = soup.find_all('div', {'data-component-type': 's-search-result'})

# looking for amount of pages
nav = soup.find('div', 'a-section a-spacing-none a-padding-base')
last_index = nav.find_all('li', {'aria-disabled': 'true'})
final_result_of_pages = int(last_index[1].text)

items = []
for page in range(2, final_result_of_pages + 1):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all('div', {'data-component-type': 's-search-result'})
    print("Scanning page #" + str(page-1) + "...")
    search(sys.argv[1], page)
    for i in results:
        item = find_info(i)
        if item:
            items.append(item)
    page += 1
print("The .csv file is ready!")
