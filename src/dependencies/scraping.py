from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from bs4 import BeautifulSoup

from time import sleep
import random

import pandas as pd

LAZADA_BASE_URL = 'https://www.lazada.co.th/'
LAZADA_PLATFORM = 'lazada'
SHOPEE_BASE_URL = 'https://shopee.co.th'
SHOPEE_PLATFORM = 'shopee'


def get_url(search_term, template):
    """Generate an url from the search term"""
    # https://www.lazada.co.th/catalog/?q=keychron+k2&_keyori=ss&from=input&spm=a2o4m.home.search.go.11257f6dISLqGn
    # template = "https://www.lazada.co.th/catalog?q={}"
    search_term = search_term.replace(' ', '+')
    # add term query to url
    url = template.format(search_term)
    # add page query placeholder
    url += '&page={}'
    return url


def fetch_lazada_items(search_term: str, driver):
    # "https://www.lazada.co.th/catalog?q={}"
    
    template = LAZADA_BASE_URL + "catalog?q={}"
    url = get_url(search_term, template)
    # driver = get_driver()
    limit_page = 5
    rows = []
    
    for page in range(0, limit_page):
        driver.get(url.format(page))
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Bm3ON")))
        except: # if not have
            driver.refresh()
            
        driver.execute_script("""
        var scroll = document.body.scrollHeight / 10;
        var i = 0;
        function scrollit(i) {
            window.scrollBy({top: scroll, left: 0, behavior: 'smooth'});
            i++;
            if (i < 10) {
            setTimeout(scrollit, 500, i);
            }
        }
        scrollit(i);
        """)
        sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.find_all('div', {'class': 'Bm3ON'}):

            link = ''
            for a in item.find_all('a', href=True):
                link = a['href']
                link = link.replace('//','https://')

            name = item.find('div', {'class': 'RfADt'})

            if name is not None:
                name = name.text.strip()
            else:
                name = None
        
            price = item.find('div', {'class': 'aBrP0'})
            if price is not None:
                price = price.find('span', {'class': 'ooOxS'}).text.strip()
            else:
                price = None
            
            sold = item.find('div', {'class': '_6uN7R'})
            if sold is not None:
                try:
                    sold = sold.find('span', {'class': '_1cEkb'}).text.strip()
                except AttributeError:
                    sold = None
            else:
                sold = None
            
            # print([name, price, link])
            rows.append([link, name, price,sold ])

    
    # save main item to temporaly storage, waiting for scraping more infomation of item
    cols_name = ['alink', 'product_name', 'price','sold']

    return pd.DataFrame(data=rows, columns=cols_name)

def get_item_info_lazada(links, driver):
    
    # driver = get_driver()
    driver.implicitly_wait(5)
    
    rows = []
    for url in links:
        driver.get(url)
        # time.sleep(random.uniform(3, 6))
        
        soup = BeautifulSoup(driver.page_source, "html.parser")

        store_name = getattr(soup.select_one('.seller-name__detail'), 'text', 'None')

        brand_name = soup.find('div', {'class': 'pdp-product-brand'})
        if brand_name is not None:
            brand_name = brand_name.find('a', {'class': 'pdp-link pdp-link_size_s pdp-link_theme_blue pdp-product-brand__brand-link'}).text.strip()
        else:
            brand_name = None

        product_option = soup.find('div', {'class': 'pdp-mod-product-info-section sku-prop-selection'})
        if product_option is not None:
            product_option = product_option.find('span', {'class': 'sku-name'}).text.strip()
        else:
            product_option = ''
            
        rating = soup.find('div', {'class': 'score'})
        if rating is not None:
            rating = rating.find('span', {'class': 'score-average'}).text.strip()
        else:
            rating = None
        
        
        platform = LAZADA_PLATFORM
        # print([url,store_name, brand_name, price_range, rating, sold, platform])
        rows.append([url,store_name, brand_name, product_option,rating, platform])
        # time.sleep(random.uniform(3, 6))

        cols_name = ['alink', 'store_name','brand_name','specification','rating','platform']
    
    df = pd.DataFrame(data=rows, columns=cols_name)
    return df



def fetch_shopee_items(search_term, driver):
    """source code: https://stackoverflow.com/questions/66747082/web-scraping-shopee-sg-with-selenium-and-beautifulsoup-in-python"""
    # driver = get_driver()
    rows = []
    template = SHOPEE_BASE_URL + "/search?keyword={}"
    url = get_url(search_term,template)
    print(url)
    limit_page = 5
    for page in range(0, limit_page):
        driver.get(url.format(page))
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "shopee-search-item-result__item")))
        
        try:
            # bot click choose thai lang button
            thai_button = driver.find_element("xpath", '/html/body/div[2]/div[1]/div[1]/div/div[3]/div[1]/button') # new version
            thai_button.click()
            # bot close popup
            # close_popup_button.click()
            # close_popup_button = driver.execute_script('return document.querySelector("shopee-banner-popup-stateful").shadowRoot.querySelector("div.shopee-popup__close-btn")')
        except NoSuchElementException:
                pass
        
        driver.execute_script("""
        var scroll = document.body.scrollHeight / 10;
        var i = 0;
        function scrollit(i) {
           window.scrollBy({top: scroll, left: 0, behavior: 'smooth'});
           i++;
           if (i < 10) {
            setTimeout(scrollit, 500, i);
            }
        }
        scrollit(i);
        """)
        sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")


        for item in soup.find_all('div', {'class': 'col-xs-2-4 shopee-search-item-result__item'}):
            link = ''
            for a in item.find_all('a', href=True):
                link = SHOPEE_BASE_URL+a['href']
            
            name = item.find('div', {'class': 'ie3A+n bM+7UW Cve6sh'})
            if name is not None:
                name = name.text.strip()
            else:
                name = ''

            price = item.find('div', {'class': 'vioxXd rVLWG6'})
            if price is not None:
                price = price.find('span', {'class': 'ZEgDH9'}).text.strip()
                price = int(float(price.replace(',','')))
            else:
                price = ''
            
            # print([name, price, link])
            rows.append([name, price, link])

    return pd.DataFrame(data=rows, columns=['product_name', 'price','alink'])


def get_item_info_shopee(links, driver):
    
    # driver = get_driver()
    driver.implicitly_wait(5)
    try:
        en_button = driver.find_element("xpath", '/html/body/div[2]/div[1]/div[1]/div/div[3]/div[2]/button') # new version
        en_button.click()
    except NoSuchElementException:
            pass
    
    rows = []
    for url in links:
        driver.get(url)
        sleep(random.uniform(3, 6))
        
        soup = BeautifulSoup(driver.page_source, "html.parser")

        store_name = getattr(soup.select_one('.VlDReK'), 'text', 'None')
        brand_name = getattr(soup.select_one('.GvvZVe'), 'text', 'None')
        price_range = getattr(soup.select_one('.pqTWkA'), 'text', 'None')
        rating = getattr(soup.select_one('._1k47d8'), 'text', 'None')
        sold = getattr(soup.select_one('.P3CdcB'), 'text', 'None')
        platform = SHOPEE_PLATFORM
        
        # print([url,store_name, brand_name, price_range, rating, sold, platform])
        rows.append([url,store_name, brand_name, price_range, rating, sold, platform])

    df = pd.DataFrame(data=rows, columns=['alink', 'store_name','brand_name','price_range','rating','sold','platform'])
    return df
