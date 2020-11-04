import aiohttp, re, time, traceback2
from bs4 import BeautifulSoup


class Filter:

    def __init__(self, filter_text, black_list, white_list):
        self.filter = filter_text
        self.black_list = black_list
        self.white_list = white_list
        self.link_match = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        self.domain_match = '(?:https?://)?(?P<host>.*?)(?:[:#?/@]|$)'
        self.result = 0

    async def execute_filter(self, message):
        await self.check_text(message)
        return self.result

    async def check_text(self, text):
        match_result = re.search(self.filter, text, flags=re.I)
        if match_result is not None:
            self.result = 1
        else:
            await self.check_link(text)

    async def check_link(self, text):
        for link in re.findall(self.link_match, text):
            await self.check_listed_link(link)

    async def check_listed_link(self, link):
        if re.search(self.white_list, link) is not None:
            self.result = 0
        elif re.search(self.black_list, link) is not None:
            self.result = 1
        else:
            await self.parse_link(link)

    async def parse_link(self, link):
        response: str
        text = ""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                async with session.get(link) as r:
                    response = await r.text()
        except:
            text += link
            await self.check_link_text(text)
        else:
            text += str(r.url)
            text += link
            soup = BeautifulSoup(response, 'html.parser')
            try:
                text += soup.title.string
            except:
                pass
            try:
                meta_desc = soup.find_all("meta", attrs={"name": "description"})
                meta = meta_desc[0].get('content')
                text += meta
            except:
                pass
            await self.check_link_text(text)

    async def check_link_text(self, text):
        match_result = re.search(self.filter, text, flags=re.I)
        if match_result is not None:
            self.result = 1

