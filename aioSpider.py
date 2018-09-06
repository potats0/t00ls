#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import asyncio
import random
import sys
from urllib.parse import urlparse, urlunparse, parse_qs

import aiohttp
from bs4 import BeautifulSoup


class crawl:
    def __init__(self, target, headers, allow_domain=True):
        self.task = []
        self.headers = headers
        self.conf = urlparse(target)
        self.task.append(target)
        self.is_allow_domain = allow_domain
        self.loop = asyncio.get_event_loop()

    def read(self, file):
        with open(file, "r") as f:
            for i in f.readlines():
                self.task.append(self.target + i)

    def parseFromtext(self, content, task_url, resp_url):
        self.url_hash[resp_url], self.url_hash[task_url] = True, True
        soup = BeautifulSoup(content, 'html.parser')
        weblist = [tag.get('href') for tag in soup.find_all('a')]
        url_list = []
        for tag in weblist:
            result = urlparse(tag)
            if result.scheme.startswith('http'):
                continue
            link = []
            link.append(self.conf.scheme if not result.scheme else result.scheme)
            link.append(self.conf.netloc if not result.netloc else result.netloc)
            if link[1] != self.conf.netloc and self.is_allow_domain:
                continue
            link.append(self.conf.path if not result.path else result.path)
            link.extend(result[3:])
            link = urlunparse(link)
            if link not in self.url_hash:
                self.url_hash[link] = False
                self.task.append(link)
                url_list.append(link)
            param = parse_qs(result.query).keys()
            query = ''.join([i for i in sorted(param)])
        return url_list

    async def fetch(self, client, task_url):
        url_list = []
        await asyncio.sleep(random.randrange(0, 4) + random.random())
        try:
            async with client.get(task_url, compress=True, timeout=5, allow_redirects=False) as resp:
                if resp.status != 200:
                    raise Exception("Http error")
                url_list = self.parseFromtext(await resp.text(), task_url, resp.url)
                print(task_url)
                self.param.append(task_url)
        except Exception:
            print("Connection reset by peer")
            sys.exit(1)
        finally:
            self.task.extend(url_list)

    def run(self):
        with aiohttp.ClientSession(loop=self.loop, headers=self.headers) as client:
            while self.task:
                u = []
                curr, self.task = self.task[0:1000], self.task[1000:len(self.task)]
                while curr > 0:
                    url = curr.pop()
                    if url in self.url_hash.keys() and self.url_hash.get(url): continue
                    u.append(self.fetch(client, url))
                if not u:
                    break
                self.loop.run_until_complete(asyncio.wait(u))
        self.loop.close()
        print("done")

    def webscan(self, file):
        self.read(file)
        self.scan = True
        return self.run()
