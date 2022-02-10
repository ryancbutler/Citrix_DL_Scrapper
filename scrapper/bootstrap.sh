#!/bin/bash
export ctxpass=$ctxpass
export ctxuser=$ctxuser

python ctxScrapper.py
cp ctx_dls* /data