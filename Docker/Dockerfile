FROM python:3.9
LABEL org.opencontainers.image.source https://github.com/ryancbutler/Citrix_DL_Scrapper

COPY /scrapper /app
WORKDIR /app

RUN mkdir __logger

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip jq
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/98.0.4758.80/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
#ENV DISPLAY=:1

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["bash", "./bootstrap.sh"]
