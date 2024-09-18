import threading
import requests
from bs4 import BeautifulSoup
import time
import enum
import os
import json
import math
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
from operator import itemgetter



class TYPES(enum.Enum):
    NONE = 0
    CATEGORY = 1
    PAGE = 2
    PRODUCT = 3
    DATA = 4


class DickiesThread(threading.Thread):
    thread_id:int = 0
    thread_type = TYPES.NONE
    thread_url:str = ""
    base_url:str="https://dickiesaustralia.com"
    data_file:str = "dickies.json"

    category_urls:list=[str]
    page_urls:list=[str]
    product_urls:list=[str]


    def __init__(self,thread_id, thread_type, thread_url ):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_type=thread_type
        self.thread_url = thread_url
       

    
    
    def requests_url(self, url):
        headers = {
            "User-Agent" : "PostmanRuntime/7.40.0",
                      
            }     
        retry_strategy = Retry(
            total=5,
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
    
   # //////////////////////////////   ctegory 
    def get_category_urls(self,soup):
        category_urls = [self.base_url + href.get("href") for menu_item in soup.find_all("li", {"class": "cc-dropdown"}) for href in menu_item.find_all("a")]
        return category_urls

    # //////////////////////////// page url
    def calculate_page_count(self,category_url):
        try:
            response = self.requests_url(category_url)
            soup=self.generate_page_soup(response.content)
            
            if soup:
                total_products = soup.find("div", {"class": "ms-auto d-none d-lg-block"}).text.strip().split(" ")[0]
                product_urls = [self.base_url + href.get("href") for href in soup.find_all("a", {"class": "item-link prod-listing-link"})]
                return math.ceil(int(total_products) / len(product_urls))
        except:
            print(f"///////////Error in calculate_page_count")
            return 1

    def scrape_page_urls(self,category_url):
        total_pages = self.calculate_page_count(category_url)
        print(total_pages)
        if total_pages is not None:
            total_pages+=1

            for page_num in range(1,total_pages):
                print(f"Scraping: {category_url}?page={page_num}")
                self.save_page_url(f"{category_url}?page={page_num}")
        else :
            self.save_page_url(f"{category_url}")
    def save_page_url(self,product_url):
        
        print("///////////////////////",self.page_urls_exist(product_url,self.load_page_urls()))
        if not self.page_urls_exist(product_url,self.load_page_urls()):
            
            loaded = {
                "page_urls": []
            }

            data_file = "page_urls.json"   


            try:
                with open(data_file) as f:
                    file_contents = json.loads(f.read())

                    for item in file_contents["page_urls"]:
                        loaded["page_urls"].append(item)

            except FileNotFoundError:
                with open(data_file, "w") as f:
                    pass

            loaded["page_urls"].append(product_url)
            with open(data_file, "w") as f:
                json.dump(loaded, f)
        else:
            return
          
    def page_urls_exist(self,product_url,exist_product_urls):
    
        return product_url in exist_product_urls["page_urls"]

    def load_page_urls(self):
        
        if not os.path.exists("page_urls.json"):
                return {"page_urls": []}
        with open("page_urls.json","rt",encoding="utf-8-sig") as json_file :
            loaded_data=json.load(json_file)
            return loaded_data
   
    # //////////////////////    get priduct url
    def get_product_urls(self,page_url):
        response = self.requests_url(page_url)
        soup=self.generate_page_soup(response.content)
        
        product_urls=soup.find_all("a",{"class":"item-link prod-listing-link"})
        for a in  product_urls:
            self.save_products_url(self.base_url+"/"+a.get("href"))
    def save_products_url(self,product_url):
        
        print("///////////////////////",self.product_urls_exist(product_url,self.load_product_urls()))
        if not self.product_urls_exist(product_url,self.load_product_urls()):
            
            loaded = {
                "product_urls": []
            }

            data_file = "product_urls.json"   


            try:
                with open(data_file) as f:
                    file_contents = json.loads(f.read())

                    for item in file_contents["product_urls"]:
                        loaded["product_urls"].append(item)

            except FileNotFoundError:
                with open(data_file, "w") as f:
                    pass

            loaded["product_urls"].append(product_url)
            with open(data_file, "w") as f:
                json.dump(loaded, f)
        else:
            return
    @staticmethod      
    def product_urls_exist(product_url,exist_product_urls):
    
        return product_url in exist_product_urls["product_urls"]
    @staticmethod
    def load_product_urls():
        
        if not os.path.exists("product_urls.json"):
                return {"product_urls": []}
        with open("product_urls.json","rt",encoding="utf-8-sig") as json_file :
            loaded_data=json.load(json_file)
            return loaded_data
    
# /////////////////////////
    def get_product_data(self,product_url):
        
        try:

            response = self.requests_url(product_url)
            soup=self.generate_page_soup(response.content)
        

            script=str(soup.find_all("script")[-2]).strip()
            items=script.split("value: 0,")[1].split("});")[0].split("items: ")[1]
            item = re.findall(r"item+.+,",items)
            data=[
                {
                    "id":item[0].split(":")[1].strip(",").strip('\" '),
                    "name":item[1].split(":")[1].strip(",").strip('\" '),
                    "brand":item[2].split(":")[1].strip(",").strip('\" '),
                    "category":item[3].split(":")[1].strip(",").strip('\" '),
                    "variant":item[4].split(":")[1].strip(",").strip('\" '),
                    "price":re.findall(r"price+.+,",items)[0].split(": ")[1].strip(),
                    "quantity":re.findall(r"quantity+.+",items)[0].split(": ")[1].strip("\r"),
                    "color":[ h.get("href").split("-")[-1]  for a in soup.find_all("div",{'class':"prod-exd-colour-size"}) for h in a.find_all("a")  if h.get("href").split("-")[-1]!='' and h.get("href").split("-")[-1]!='#'],
                    
                }
            ]
            print(data)
            self.save_data(data)


    
        except:
            print("None")
            return "None"
    

    def save_data(self,data):      

    
        loaded = {
                "products": []
        }

        data_file = "d.json"  


        try:
            with open(data_file) as f:
                file_contents = json.loads(f.read())

                for item in file_contents["products"]:
                    loaded["products"].append(item)

        except FileNotFoundError:
            with open(data_file, "w") as f:
                pass

        loaded["products"].append(data)
        with open(data_file, "w") as f:
            json.dump(loaded, f)
       


    def product_exist(products,product):
        product_ids=list(map(itemgetter("id"),products["products"]))
        if product["id"] in product_ids:
            return True
        else:
            return False
        
    def load_products():
        if not os.path.exists("d.json"):
            return {"products": []}
        with open("d.json","rt",encoding="utf-8-sig") as json_file :
            loaded_data=json.load(json_file)
            return loaded_data
    
    # @staticmethod
    def load_products(self):
        if not os.path.exists(self.data_file):
            return {"products": []}
        with open(self.data_file,"rt",encoding="utf-8-sig") as json_file :
            loaded_data=json.load(json_file)
            return loaded_data


    # /////////////////////////////////////
    

    def run(self):
        if self.thread_type == TYPES.CATEGORY:
            print("______HOMEPAGE_____")
            
            response = self.requests_url(self.thread_url)
            soup=self.generate_page_soup(response.content)
            if soup:
                DickiesThread.category_urls=self.get_category_urls(soup)
           
            else:
                print("-----")
            
        if self.thread_type == TYPES.PAGE:
            print("______PAGE_____")
            if isinstance(self.thread_url,str):

                self.scrape_page_urls(self.thread_url) 
                DickiesThread.page_urls=self.load_page_urls()["page_urls"]
            else:
                print("----") 
        
        if self.thread_type == TYPES.PRODUCT  :
            print("______PRODUCT_____")
            if isinstance(self.thread_url,str):
                self.get_product_urls(self.thread_url)
                DickiesThread.product_urls=self.load_product_urls()["product_urls"]
            else:
                print("----")
        if self.thread_type == TYPES.DATA  :
            print("______DATA_____")
            if isinstance(self.thread_url,str):
                self.get_product_data(self.thread_url)
               
            else:
                print("----")

       

