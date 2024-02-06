#!/usr/bin/python3

from calendar import c
from cgi import test
import json
from time import sleep, time
from typing import Any, Callable, Dict, Tuple
from quickhttp import httpconst
from quickhttp import content_codec as http_codec
from quickhttp.connection import ConnBuilder, HttpConn
from quickhttp.request import HttpReqData
from quickhttp.response import HttpRespData
from quicktest.expect_test import quick_assert
from quicktest.names import ROOT, ACCEPT, API, REQ_BODY, EXPECT, CASE
from bs4 import BeautifulSoup


builder = ConnBuilder(httpconst.HTTP, "www.5shuzhai.com", httpconst.HTTPPORT)

pages = [i+10762663 for i in range(90)]
pages.reverse()
# http: // www.5shuzhai.com/chapter/10762752.html
for page in pages:
    conn_case = builder.build(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0')

    loginReq = HttpReqData()
    loginReq.request('/chapterList/11337.html', httpconst.METHOD_GET,
                     "/chapter/{}.html".format(page), None)

    loginReq.send({
        "Cookie":
        " __vtins__JgCF8322MP4NNIrv=%7B%22sid%22%3A%20%2250e7bd42-b38c-58bd-9783-4ed2e3453574%22%2C%20%22vd%22%3A%202%2C%20%22stt%22%3A%2071179%2C%20%22dr%22%3A%2071179%2C%20%22expires%22%3A%201663752847597%2C%20%22ct%22%3A%201663751047597%7D; __51uvsct__JgCF8322MP4NNIrv=4; __51vcke__JgCF8322MP4NNIrv=2a340578-fe22-5399-b3f5-d8e92d38edb3; __51vuft__JgCF8322MP4NNIrv=1663731869550",
        "Upgrade-Insecure-Requests": " 1",
        "Connection": " keep-alive"
    }, None, None)

    loginReq.set_acceptings('text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                            'gzip, deflate, br',
                            'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2')
    resp = conn_case.do_request(loginReq)
    print("down chapter:{},status code:{}".format(page, resp.statuscode()))
    htmlDoc = resp.receive(http_codec.RspToHTML)

    with open("./{}.html".format(page), "w", buffering=1024, encoding='utf-8') as wr:
        wr.write(htmlDoc)
    print("save {}.html chapter:{}".format(page, page-10762663+1))

    sleep(10)
    conn_case.close()
