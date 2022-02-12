#!/bin/bash
export ctxpass=$ctxpass
export ctxuser=$ctxuser
cp /data/ctxScrapper.py ./
python ctxScrapper.py
cp ctx_dls* /data