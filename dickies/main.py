import time
import os
import DickiesThread as Th

if __name__ == "__main__":
    

    base_url="https://dickiesaustralia.com"
    
   
    category_thread=Th.DickiesThread(thread_id=1,thread_type=Th.TYPES.CATEGORY,thread_url=base_url)
    category_thread.start()
    category_thread.join()
    category_urls=Th.DickiesThread.category_urls
    print(len(category_urls))

    threads = []
    end_category=False
    print("................................................................")


  
    for id in range(len(category_urls)):
        if category_urls:
            category_url = category_urls.pop(0)
            page_thread = Th.DickiesThread(thread_id=id, thread_type=Th.TYPES.PAGE, thread_url=category_url)
            threads.append(page_thread)
            page_thread.start()
            time.sleep(0.5)


    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    
    page_urls=Th.DickiesThread.page_urls 
    for id in range(len(page_urls)):
        if page_urls:
            page_url=page_urls.pop(0)
            product_thread=Th.DickiesThread(thread_id=id,thread_type=Th.TYPES.PRODUCT,thread_url=page_url)
            threads.append(product_thread)
            product_thread.start()
            time.sleep(0.5)
    print("********************************")
    product_urls=Th.DickiesThread.load_product_urls()["product_urls"] 
    for id in range(len(product_urls)):
        if product_urls:
            product_url=product_urls.pop(0)
            data_thread=Th.DickiesThread(thread_id=id,thread_type=Th.TYPES.DATA,thread_url=product_url)
            threads.append(data_thread)
            data_thread.start()
            time.sleep(2)





    for thread in threads:
        thread.join()

            
print("end")

