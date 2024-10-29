import requests
import threading
from operator import itemgetter
import time
from bs4 import BeautifulSoup
import json
import math
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import os
import re
import enum

class RequestType(enum.Enum):
    NONE = "none"
    PRODUCT = "product"
    DATA = "data"
    
class Amiri(threading.Thread):

    
    def __init__(self, thread_id, request_type, thread_url):
        super().__init__()
        self.thread_id = thread_id
        self.request_type = request_type
        self.thread_url = thread_url


    def requests_url(self, url):

        headers = {
            "User-Agent" : "PostmanRuntime/7.40.0",
                      
            }     
        retry_strategy = Retry(
            total=7,
            status_forcelist=[429, 500, 502, 503, 504, 400],
            allowed_methods=["GET", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        try:
            response = session.get(url, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


    
    def generate_page_soup(self,content):
        soup = BeautifulSoup(content, "html.parser")
        return soup
    

    def save_to_file(self, filename, value):
       
        data = {filename: []}
        if os.path.exists(f"{filename}.json"):
            with open(f"{filename}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
        if value not in data[filename]:
            data[filename].append(value)
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f)
   
   
    @staticmethod
    def load_from_file(filename):
        if not os.path.exists(filename):
            return {filename: []}
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_products_url(self,category_url):
        page_number=0
        while True:
            page_number+=1
            
            try:
                response = self.requests_url(category_url+str(page_number))
                soup=self.generate_page_soup(response.content)
                product_urls=["https://amiri.com"+i.get("href") for i in soup.find_all("a",{'class':"product-card"})]
            
                self.save_to_file("product_urls",product_urls)
                print(len(product_urls))
                if len(product_urls) <=2:
                    break
               
            except:
                self.save_to_file("category_failed",category_url+str(page_number))
                print("error")



    def get_product_data(self,url):
        try:
            response = self.requests_url(url)
            soup=self.generate_page_soup(response.content)
            
            regex = r'ProductID:\s*(\d+),\s*Categories:\s*\[([^\]]+)\]'
            match = re.search(regex, (str(soup.find("script",{"id":"viewed_product"}))))
            if match:
            
                product_id = match.group(1)
                categories = [category.strip().strip('"') for category in match.group(2).split(',')]
                


            data={
                "product_id":product_id,
                "name":soup.find("h1", {"class": "product__title h5"}).text.strip(),
                "categories":categories,
                "color":soup.find("span", {"class": "product__info-subdetails-color flex aic"}).text.strip(),
                "sizes":[size.text.strip() for size in soup.find_all("div", {"class": "variant-option-wrapper sortable"})],
                "price":soup.find("div", {"class": "product__info-subdetails-price-color flex jcc aic"}).find("span", {"class": "price-item price-item--regular"}).text.strip(),
                "product_descriptions":soup.find("div", {"class": "product__description"}).text.strip(),
                "care_size_and_fits":[fit.text.strip() for fit in soup.find_all("div", {"class": "metafield-rich_text_field"})],
                "images":["https:"+li.find("img").get("src") for li in soup.find_all("li", {"class": "splide__slide media-ratio product__media-item"})]
            } 

            print(data)
            self.save_to_file("products",data)


 
        except:
            self.save_to_file("faild_url",url)
            print("None")
            return "none"


        
    
    def dispatch(self):
        dispatch_map = {
            RequestType.PRODUCT: self.get_products_url,
            RequestType.DATA: self.get_product_data,
        }
        method = dispatch_map.get(self.request_type, lambda: None)
        method(self.thread_url)
    
    def run(self):
        self.dispatch()

