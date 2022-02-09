# Scraps Citrix.com for needed download information to be used for https://github.com/ryancbutler/Citrix/tree/master/XenDesktop/AutoDownload
# Ryan Butler 2/8/2022 @ryan_c_butler
# Needs Chrome and ChromeDriver to be installed
#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    "a", {"href": re.compile('^(?!.*x\.html)(?=.*downloads\/c)(?!.*\.rss).*')})

for dl in dls_selector:
    dls.append(dl['href'])

f = open('../ctx_dls.csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(f)
writer.writerow(['edition', 'product', 'version', 'checksum',
                'date', 'dlnumber', 'url', 'filename', 'filetype', 'size', 'family'])

ctxDLS = []
for ctxDL in dls:
    driver.get('https://www.citrix.com' + ctxDL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    dl_sections = soup.find_all("div", {"class": "ctx-download-entry"})
    for dl_section in dl_sections:
        dl_type = (dl_section.find("span", {"class": "dl-type"})).text
        if dl_type == "(.htm)":
            print("HTML DL TYPE FOUND. Skipping")
        else:
            dl_product = (dl_section.find("h4")).text
            dl_url = dl_section.a['rel'][0]
            dl_size = (dl_section.find("span", {"class": "dl-size"})).text
            dl_date = (dl_section.find("span", {"class": "ctx-dl-langs"})).text
            dl_checksum_list = dl_section.find(
                "ul", {"class": "ctx-checksum-list"})

            if dl_checksum_list is None:
                dl_checksum = "NONE"
            else:
                dl_checksum = (dl_checksum_list.find("li")).text

            filename = (dl_url.split('/')[-1])
            edition = (driver.title).replace(", All Editions - Citrix", "")
            dlid = re.findall('(?<=DLID=)(.*)(?=&)', dl_url)[0]
            version = re.search('((7\.)\d\d)|(\d\d\d\d)',
                                driver.title)
            filetype = filename.split('.')[-1]

            print(dl_product)
            writer.writerow(
                [edition, dl_product, version[0], dl_checksum, dl_date, dlid, dl_url, filename, filetype, dl_size, 'cvad'])

            ctxDLS.append({"edition": edition, "product": dl_product,
                           "version": version[0], "checksum": dl_checksum, "date": dl_date, "dlnumber": dlid, "url": dl_url, "filename": filename, "filetype": filetype, "size": dl_size, "family": 'cvad'})


with open('../ctx_dls.json', 'w', encoding='utf-8') as f:
    json.dump(ctxDLS, f, ensure_ascii=False, indent=4)

# Close CSV
f.close()
driver.quit()
