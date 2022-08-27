from __future__ import absolute_import, unicode_literals
from celery import Celery, shared_task
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from .email import send_review_email
from .models import Ad

app = Celery('tasks')


@app.task(bind=True)
def ads_mining(self,key,sample_size,email):
    PATH= "../geckodriver"
    binary = '/usr/bin/firefox'
    options = webdriver.FirefoxOptions() 
    options.binary = binary
    options.headless = True
    profile = webdriver.FirefoxProfile()
    count = 0 #Init count for Ads "Will print total count"
    page_no = 1 #Init page number
    actual=0 #Init count for Ads "Will print actual count of the used Ads"
    print('=================================================================================')
    print('OLX Scrap Started')
    print('============================================')
    driver= webdriver.Firefox(firefox_options=options,executable_path=PATH,firefox_profile=profile)
    driver.maximize_window()
    driver.get("https://www.olx.com.eg/en/")
    driver.implicitly_wait(10) #seconds
    searchbar = driver.find_element_by_xpath("//input[@type='search']")
    searchbar.send_keys(key)
    searchbutton = driver.find_element_by_xpath("//button[@class='_0db6bd2f a3e390b5']")
    searchbutton.click()
    driver.implicitly_wait(10) #seconds
    main_url = driver.current_url #Main URL after search

    def data_mining(count, actual, page_no, key=key, main_url=main_url, size= sample_size, email= email):
        print('=================================================================================')
        print('MAIN URL PAGE:', main_url+f"?page={page_no}")
        print('============================================')
        results_batch = driver.find_elements_by_xpath("//li[@aria-label='Listing']/article[contains(@class, '_7e3920c1')]/div[contains(@class, 'a52608cc')]/a")
        links_hrefs = [link.get_attribute('href') for link in results_batch]

        count += len(links_hrefs)
        rem = 300 - count
        print('=================================================================================')
        print('RESULT COUNT IN ITERATIONS', count)
        print('============================================')
        
        init_id=0 #start of queryset, will be updated with first iteration

        for i in range(len(links_hrefs)):
            # if rem < 0:
            #     if i == len(links_hrefs) + rem:
            #         break
            driver.implicitly_wait(10) #seconds   
            driver.get(links_hrefs[i])
            try:
                driver.implicitly_wait(10) #seconds
                price= driver.find_element_by_xpath("//span[@class='_56dab877']").text
                print('=================================================================================')
                print('PRICE', price)
                print('============================================')
            except:
                count -= 1
                print('=================================================================================')
                print('Updated COUNT', count)
                print('============================================')
                continue
            loc =  driver.find_element_by_xpath("//span[contains(@class, '_8918c0a8')][1]").text
            print('=================================================================================')
            print('Location', loc)
            print('============================================')
            title =  driver.find_element_by_xpath("//h1[contains(@class, 'a38b8112')]").text
            print('=================================================================================')
            print('title', title)
            print('============================================')
            name = driver.find_element_by_xpath("//div[contains(@class, '_1075545d _6caa7349 _42f36e3b d059c029')]/span[contains(@class, '_261203a9 _2e82a662')]").text
            print('=================================================================================')
            print('name', name)
            print('============================================')
            description = driver.find_element_by_xpath("//div[@class= '_0f86855a']/span").text
            print('=================================================================================')
            print('Desc', description)
            print('============================================')
            details= driver.find_elements_by_xpath("//div[contains(@class, '_676a547f')]")
            details_list= []
            for i in details:
                details_list.append(i.text)   
            
            print('=================================================================================')
            print('Details list:', details_list)
            print('============================================')

            try:
                extra = driver.find_elements_by_xpath("//span[contains(@class, '_66b85548')]")
                extras_list= []
                for i in extra:
                    extras_list.append(i.text)
                print('=================================================================================')
                print('Extras', extras_list)
                print('============================================')
                new_ad= Ad.objects.create(
                    keyw = key,
                    price = int(price.split(" ")[1].replace(",","")),
                    location = loc,
                    title = title,
                    owner_name = name,
                    description = description,
                    details = {
                        i.split("\n")[0]:i.split("\n")[1] for i in details_list
                    },
                    extra = extras_list
                    
                )
            except:
                new_ad= Ad.objects.create(
                    keyw = key,
                    price = int(price.split(" ")[1].replace(",","")),
                    location = loc,
                    title = title,
                    owner_name = name,
                    description = description,
                    details = {
                        i.split("\\n")[0]:i.split("\\n")[1] for i in details_list
                    }                    
                )
                print('=================================================================================')
                print('No Extras')
                print('============================================')
            actual+=1
            new_ad.save()
            print('=================================================================================')
            print('ACTUAL COUNT:', actual)
            print('============================================')
            
            
            if i == 0:
                #save id of the first query
                init_id= new_ad.id 
            
            if actual == int(size):
                queryset = Ad.objects.filter(id__gt = init_id-1, id__lt= init_id+int(size)+1).order_by("-price")
                x = send_review_email(queryset,email)
                print("EMAIIIIIIIIIL",x)
        
        if count < 300:
            
            page_no+=1
            driver.get(main_url + f"?page={page_no}")
            data_mining(count, actual, page_no)
    

    data_mining(count,actual,page_no) #Start data mining & the operations coming with it.