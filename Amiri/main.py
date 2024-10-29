from concurrent.futures import ThreadPoolExecutor
import AmiriThread as Th
import time
if __name__ == "__main__":
    threads = []
    # base_url=""
    category_urls=[
        "https://amiri.com/collections/men?page=",
        "https://amiri.com/en-de/collections/women?page=",
        "https://amiri.com/en-de/collections/kids?page=",
        "https://amiri.com/en-de/collections/footwear?page=",
        "https://amiri.com/en-de/collections/accessories?page="
        ]



    # for id in range(len(category_urls)):
    #     if category_urls:
    #         category_url = category_urls.pop(0)
    #         print(id)

    #         product_thread = Th.Amiri(thread_id=id, request_type=Th.RequestType.PRODUCT, thread_url=category_url)
    #         threads.append(product_thread)
    #         product_thread.start()
    #         time.sleep(0.5)


    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

    product_urls=Th.Amiri.load_from_file("product_urls.json")["product_urls"]
    print(len(product_urls))
    for pr_urls in product_urls:
        for id in range(len(pr_urls)):

            if pr_urls:
                product_url = pr_urls.pop(0)
                print(id)
                print(product_url)

                product_data_thread = Th.Amiri(thread_id=id, request_type=Th.RequestType.DATA, thread_url=product_url)
                threads.append(product_data_thread)
                product_data_thread.start()
                time.sleep(5)
 

    

    for thread in threads:
        thread.join()



print("end")

