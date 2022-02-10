# Citrix Download Scrapper

Python script the scrapes Citrix.com for needed download info for download scripts such as <https://github.com/ryancbutler/Citrix/tree/master/XenDesktop/AutoDownload>

## How to use

From scrapper directory

1. Install Chrome
2. Install Chromedriver <https://chromedriver.chromium.org/downloads>
3. Install requirements `pip3 install -r ./scrapper/requirements.txt`
4. Set login credentials as environmental variables

```bash
export ctxuser="MYUSERNAME"
export ctxpass="MYPASSWORD"
```

5. Run `python3 ctxScrapper.py`

## Docker

```bash
export ctxuser="MYUSERNAME"
export ctxpass="MYPASSWORD"

docker build . -t ctxscrapper -f ./Docker/Dockerfile
docker run -e ctxuser -e ctxpass -v ${PWD}/data:/data ctxscrapper
```
