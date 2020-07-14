# -*- coding: utf-8 -*-

from lncrawl.app import (Author, AuthorType, Chapter, Context, Language,
                         SoupUtils, TextUtils, UrlUtils, Volume)
from lncrawl.app.scraper import Scraper


class WwwNovelhallCom(Scraper):
    version: int = 1
    base_urls = ['https://www.novelhall.com/']

    def login(self, ctx: Context) -> bool:
        pass

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        ctx.language = Language.ENGLISH

        # Parse novel
        ctx.novel.name = SoupUtils.select_value(
            soup, "#main div.container div.book-main.inner.mt30 div.book-info h1")
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(
            soup, "#main div.container div.book-main.inner.mt30 div.book-img.hidden-xs img", attr="src")
        ctx.novel.details = str(soup.select_one(
            "#main div.container div.book-main.inner.mt30 div.book-info div.intro span.js-close-wrap")).strip()

        # Parse authors
        _author = soup.select_one(
            "#main div.container div.book-main.inner.mt30 div.book-info div.total.booktag span.blue")
        _author = str(list(_author.children)[0])
        _author = _author.replace(r'Author', '').strip()
        _author = TextUtils.ascii_only(_author)
        ctx.authors.add(Author(_author, AuthorType.AUTHOR))

        # Parse volumes and chapters
        for serial, a in enumerate(soup.select("#morelist li a")):
            volume = ctx.add_volume(1 + serial // 100)
            chapter = ctx.add_chapter(serial, volume)
            chapter.body_url = a['href']
            chapter.name = TextUtils.sanitize_text(a.text)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select("#htmlContent")
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])