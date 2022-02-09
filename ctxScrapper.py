# Scraps Citrix.com for needed download information to be used for https://github.com/ryancbutler/Citrix/tree/master/XenDesktop/AutoDownload
# Ryan Butler 2/8/2022 @ryan_c_butler
# Needs Chrome and ChromeDriver to be installed
#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import csv
import json
import os

options = webdriver.ChromeOptions()
options.headless = True
options.add_experimental_option("detach", True)

# Citrix login
username = os.environ.get('ctxuser')
if username is None:
    raise EnvironmentError("Failed because ctxuser is not set.")

password = os.environ.get('ctxpass')
if password is None:
    raise EnvironmentError("Failed because ctxpass is not set.")

# Chrome driver https://chromedriver.chromium.org/downloads
driver = webdriver.Chrome(options=options)

driver.get(
    'https://identity.citrix.com/Utility/STS/Sign-In?ReturnUrl=%2fUtility%2fSTS%2fsaml20%2fpost-binding-response'
)

# login
driver.find_element_by_id("userName").send_keys(username)
driver.find_element_by_id("password").send_keys(password)
driver.find_element_by_id("idSubmit").click()

# Strange workaround for authentication
driver.get(
    'https://www.citrix.com/downloads/citrix-virtual-apps-and-desktops/product-software/'
)
WebDriverWait(driver,
              10).until(EC.title_is("Download Product Software - Citrix"))
driver.find_element_by_link_text(
    "Sign In to access restricted downloads").click()

WebDriverWait(driver,
              10).until(EC.title_is("Download Product Software - Citrix"))
page_source = driver.page_source

soup = BeautifulSoup(page_source, 'html.parser')
dls = []
dls_selector = soup.find_all(
    "a", {"href": re.compile('^(?=.*downloads\/c)(?!.*\.rss).*')})
# "a", {"href": re.compile('^(?!.*x\.html)(?=.*downloads\/c)(?!.*\.rss).*')})
for dl in dls_selector:
    dls.append(dl['href'])

f = open('ctx_dls.csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(f)
writer.writerow(['version', 'edition', 'dlnumber', 'url', 'filename', 'type'])

ctxDLS = []
for ctxDL in dls:
    driver.get('https://www.citrix.com' + ctxDL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    dls_selector = soup.find_all("a", {"rel": re.compile('^(?=.*DLID=).*')})
    for dl in dls_selector:
        print(dl['rel'])
        m = re.findall('(?<=DLID=)(.*)(?=&)', dl['rel'][0])
        exename = (dl['rel'][0].split('/')[-1])
        version = re.search('((7\.)\d\d)|(\d\d\d\d)',
                            driver.title)
        title = (driver.title).replace(", All Editions - Citrix", "")
        writer.writerow(
            [version[0], title, m[0], dl['rel'][0], exename, 'cvad'])
        ctxDLS.append({"version": version[0], "edition": title,
                      "dlnumber": m[0], "url": dl['rel'][0], "filename": exename, "type": 'cvad'})

with open('ctx_dls.json', 'w', encoding='utf-8') as f:
    json.dump(ctxDLS, f, ensure_ascii=False, indent=4)

# Close CSV
f.close()
driver.quit()
