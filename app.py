import os
import random
import re

import jinja2
from actor import (
    AutoHandler,
    regex_path,
    HTMLResponseFactory,
    resolve_mobile,
    ABCResponse,
)

from response import ArticleResponse, Article, gen_search_response
from snippets import all_articles
import snippets

SEARCH_PATH = re.compile(r"/search/(.+)")
SUBARTICLE = re.compile(r"\.article$")


class Handler(AutoHandler):
    def __init__(self):
        self.factory = HTMLResponseFactory([Handler.getpath("templates")])
        snippets.getpath = self.getpath

    @regex_path("^/$")
    @resolve_mobile
    async def handler_index(self, _: str, headers: dict, mobile: bool):
        return ArticleResponse(self.factory, "Main", Handler.getpath("html"), mobile)

    @regex_path(r"/wiki/all")
    @resolve_mobile
    async def handler_all(self, _: str, headers: dict, mobile: bool):
        response = ArticleResponse(self.factory, "all", Handler.getpath("html"), mobile)
        template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(
            response.body.decode()
        )

        response.body = template.render(
            get_articles=all_articles, article=Article("Search results", [], "", "", {})
        ).encode("utf-8")
        return response

    @regex_path(r"/wiki/(.+)")
    @resolve_mobile
    async def handler_article(self, _: str, headers: dict, name: str, mobile: bool):
        a = name.lower()
        return ArticleResponse(self.factory, a, Handler.getpath("html"), mobile)

    @regex_path("/random")
    async def handler_random(self, _: str, headers: dict):
        articles = [
            a
            for a in os.listdir(Handler.getpath("docs/articles"))
            if a.islower() and not a.startswith("_")
        ]
        a = re.sub(SUBARTICLE, "", random.choice(articles))
        return self.factory.form("redirect.html", {"url": f"/wiki/{a}"})

    @regex_path(r"/search/(.+)")
    @resolve_mobile
    async def handler_search(self, _: str, headers: dict, search: str, mobile: bool):
        found_articles = []

        for a in [
            a
            for a in os.listdir(Handler.getpath("docs/articles"))
            if a.islower() and not a.startswith("_")
        ]:
            text = open(Handler.getpath(f"docs/articles/{a}")).read()
            if all([w.lower() in text.lower() for w in search.split()]):
                found_articles.append((re.sub(SUBARTICLE, "", a), text.split("\n")[0]))

        return gen_search_response(self.factory, search, found_articles, mobile)

    async def undefined(self, path: str, headers: dict) -> ABCResponse:
        return self.factory.form("redirect.html", {"url": "/"})


if __name__ == "__main__":
    print("wiki should be ran with actor")
