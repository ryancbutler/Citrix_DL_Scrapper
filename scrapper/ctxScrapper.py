#!/usr/bin/env python3

# Scrapes Citrix.com for needed download information to be used for https://github.com/ryancbutler/Citrix/tree/master/XenDesktop/AutoDownload
# Ryan Butler 2/8/2022 @ryan_c_butler
# Needs Chrome and ChromeDriver to be installed

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import csv
import json
import os


def parse_page(page_source, family):
    soup = BeautifulSoup(page_source, 'html.parser')
    dls = []
    dls_selector = soup.find_all(
        "a", {"href": re.compile('^(?!.*x\.html)(?=.*downloads\/\w)(?!.*\.rss).*')})

    for dl in dls_selector:
        dls.append(dl['href'])

    ctxDLS = []
    for ctxDL in dls:
        driver.get('https://www.citrix.com' + ctxDL)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        dl_sections = soup.find_all("div", {"class": "ctx-download-entry"})
        for dl_section in dl_sections:
            print('https://www.citrix.com' + ctxDL)
            dl_type = (dl_section.find("span", {"class": "dl-type"}))
            if dl_type:
                dl_type = dl_type.text
            else:
                dl_type = "NONE"

            if dl_type == "(.htm)":
                print("HTML DL TYPE FOUND. Skipping")
            else:
                dl_product = (dl_section.find("h4"))
                if dl_product:
                    dl_product = dl_product.text
                else:
                    dl_product = "NONE"

                print(dl_product)
                dl_url = dl_section.a['rel'][0]

                dl_size = (dl_section.find("span", {"class": "dl-size"}))
                if dl_size:
                    dl_size = dl_size.text
                else:
                    dl_size = "NONE"

                dl_date = (dl_section.find(
                    "span", {"class": "ctx-dl-langs"}))

                if dl_date:
                    dl_date = dl_date.text
                else:
                    dl_date = "NONE"

                dl_checksum_list = dl_section.find(
                    "ul", {"class": "ctx-checksum-list"})

                if dl_checksum_list:
                    dl_checksum = (dl_checksum_list.find("li")).text
                else:
                    dl_checksum = "NONE"

                filename = (dl_url.split('/')[-1])
                edition = (driver.title).replace(", All Editions - Citrix", "")

                dlid = (re.search(
                    '(?<=DLID=)(.*)(?=&)|(?<=DLCID=)(.*)(?=&)', dl_url))
                if dlid:
                    dlid = dlid.group()
                else:
                    dlid = "NONE"
                    print("DLID NOT FOUND")

                if dlid != "NONE":
                    # Versions with multiple matches
                    if family == "adc":
                        version = re.search(
                            '(\d{1,}\.\d+)( Build )(\d\d*\.\d{1,})|(\d{1,}\.\d{0,})|(\d{1,})', dl_product)
                    else:
                        if re.search('(\d{4})', driver.title):
                            version = re.search('(\d{4})', driver.title)
                        else:
                            version = re.search('(7\.*\d*)', driver.title)

                    if version:
                        version = version.group()
                    else:
                        version = "NONE"

                    filetype = filename.split('.')[-1]

                    # Debug
                    print(dl_product)
                    print(edition)
                    print(dl_product)
                    print(version)
                    print(dl_checksum)
                    print(dl_date)
                    print(dlid)
                    print(filename)
                    print(filetype)
                    print(dl_size)
                    print(family)
                    temp = ({"edition": edition, "product": dl_product,
                            "version": version, "checksum": dl_checksum, "date": dl_date, "dlnumber": dlid, "url": dl_url, "filename": filename, "filetype": filetype, "size": dl_size, "family": family})

                    ctxDLS.append(temp)
    return ctxDLS


options = webdriver.ChromeOptions()
options.headless = True
options.add_experimental_option("detach", True)
# Disabling warning that browser is controlled by software.
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_argument('--disable-infobars')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--no-first-run')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-client-side-phishing-detection')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--disable-web-security')
options.add_argument("--log-level=3")

# Citrix login
username = os.environ.get('ctxuser')
if username is None:
    raise EnvironmentError("Failed because ctxuser is not set.")

password = os.environ.get('ctxpass')
if password is None:
    raise EnvironmentError("Failed because ctxpass is not set.")


# Chrome driver https://chromedriver.chromium.org/downloads
driver = webdriver.Chrome(options=options)

print("Begining LOGIN")
driver.get(
    'https://identity.citrix.com/Utility/STS/Sign-In?ReturnUrl=%2fUtility%2fSTS%2fsaml20%2fpost-binding-response'
)

# login
driver.find_element_by_id("userName").send_keys(username)
driver.find_element_by_id("password").send_keys(password)
driver.find_element_by_id("idSubmit").click()
# Strange workaround for authentication
print("Waiting for login")
driver.get(
    'https://www.citrix.com/downloads/citrix-virtual-apps-and-desktops/product-software/'
)
WebDriverWait(driver,
              10).until(EC.title_is("Download Product Software - Citrix"))
driver.find_element_by_link_text(
    "Sign In to access restricted downloads").click()
WebDriverWait(driver,
              10).until(EC.title_is("Download Product Software - Citrix"))

final = []
print("Begining PARSING")
driver.get(
    'https://www.citrix.com/downloads/citrix-virtual-apps-and-desktops/product-software/'
)
WebDriverWait(driver,
              10).until(EC.title_is("Download Product Software - Citrix"))
final += parse_page(driver.page_source, "cvad")

driver.get(
    'https://www.citrix.com/downloads/provisioning-services/'
)
WebDriverWait(driver,
              10).until(EC.title_is("Download Citrix Provisioning - Citrix"))

final += parse_page(driver.page_source, "pvs")

driver.get(
    'https://www.citrix.com/downloads/citrix-adc/'
)
WebDriverWait(driver,
              10).until(EC.title_is("Download Citrix ADC - Citrix"))

final += parse_page(driver.page_source, "adc")

print("Writing files")
with open('./ctx_dls.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=4)

keys = final[0].keys()
a_file = open('./ctx_dls.csv', 'w', newline='', encoding='utf-8')
dict_writer = csv.DictWriter(a_file, keys)
dict_writer.writeheader()
dict_writer.writerows(final)
a_file.close()

driver.quit()
