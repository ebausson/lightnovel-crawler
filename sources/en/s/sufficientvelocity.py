# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class SufficientVelocity(Crawler):
    base_url = "https://forums.sufficientvelocity.com"

    def initialize(self):
        self.init_executor(1)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # Site has no author name or novel covers.
        possible_title = soup.select_one("h1.p-title-value")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = soup.select_one("a.username span").text.strip()
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one("span.avatar img")["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)
        self.crawl_chapter_list()


    def crawl_chapter_list(self):
        threadmarkPageCounter = 0
        threadmarksLastLoop = 8
        while (threadmarksLastLoop > 0):
            threadmarksLastLoop = 0
            minChapter = str(threadmarkPageCounter*100 -1)
            maxChapter = str(threadmarkPageCounter*100 + 99)
            threadmarkTempUrl = self.novel_url + "/threadmarks-load-range?threadmark_category_id=1&min=" + minChapter + "&max=" + maxChapter
            threadmarkSoup = self.get_soup(threadmarkTempUrl)
            for a in threadmarkSoup.select(".structItem-title ul li a"):
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": 1,
                        "title": a.text.strip(),
                        "url": self.absolute_url(a["href"]),
                    }
                )
                threadmarksLastLoop += 1
            threadmarkPageCounter += 1



    def download_chapter_body(self, chapter):
        post_id = chapter["url"].split("#")[1]
        page_url = chapter["url"].split("#")[0]
        soup = self.get_soup(chapter["url"])
        contents = soup.find("div", {"data-lb-id": post_id}).select_one("article").select_one("div.bbWrapper")
        return self.cleaner.extract_contents(contents)