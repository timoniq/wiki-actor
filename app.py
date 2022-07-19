import os
import random
import re
import json
import uuid

import aiofiles
import jinja2
from actor import (
    AutoHandler,
    regex_path,
    HTMLResponseFactory,
    resolve_mobile,
    ABCResponse,
    Request,
    Response
)

import generator
from response import ArticleResponse, Article, gen_search_response
from snippets import all_articles
import snippets
import json

SEARCH_PATH = re.compile(r"/search/(.+)")
SUBARTICLE = re.compile(r"\.article$")


class Handler(AutoHandler):
    def __init__(self):
        self.factory = HTMLResponseFactory([Handler.getpath("templates")])
        self.editor_factory = HTMLResponseFactory([Handler.getpath("editor/html")])
        self.factory.jinja_env.globals["config"] = json.load(open(Handler.getpath("config.json")))
        self.editor_default_contents = open(Handler.getpath("EDITOR_DEFAULT"), "r").read()
        snippets.getpath = self.getpath

        with open(Handler.getpath("config.json")) as config_file:
            self.config = json.load(config_file)

    @regex_path("^/$")
    @resolve_mobile
    async def handler_index(self, request: Request, mobile: bool):
        return ArticleResponse(self.factory, "Main", Handler.getpath("html"), mobile)

    @regex_path(r"/wiki/all")
    @resolve_mobile
    async def handler_all(self, request: Request, mobile: bool):
        response = ArticleResponse(self.factory, "all", Handler.getpath("html"), mobile)
        template = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(
            response.body.decode()
        )

        response.body = template.render(
            get_articles=all_articles, article=Article("Search results", [], "", "", {}),
            config=self.config
        ).encode("utf-8")
        return response

    @regex_path(r"/wiki/(.+)")
    @resolve_mobile
    async def handler_article(self, request: Request, name: str, mobile: bool):
        a = name.lower()
        return ArticleResponse(self.factory, a, Handler.getpath("html"), mobile)

    @regex_path("/random")
    async def handler_random(self, request: Request):
        articles = [
            a
            for a in os.listdir(Handler.getpath("docs/articles"))
            if a.islower() and not a.startswith("_")
        ]
        a = re.sub(SUBARTICLE, "", random.choice(articles))
        return self.factory.form("redirect.html", {"url": f"/wiki/{a}"})

    @regex_path(r"/search/(.+)")
    @resolve_mobile
    async def handler_search(self, request: Request, search: str, mobile: bool):
        found_articles = []

        for a in [
            a
            for a in os.listdir(Handler.getpath("docs/articles"))
            if a.islower() and not a.startswith("_")
        ]:
            text = open(Handler.getpath(f"docs/articles/{a}")).read()
            if all([w.lower() in text.lower() for w in search.split()]):
                found_articles.append((re.sub(SUBARTICLE, "", a), text.split("\n")[0]))

        return gen_search_response(self.factory, search, found_articles, self.config, mobile)

    @regex_path("/editor/([^/]+)/update")
    async def handler_editor_update(self, request: Request, uu: str):
        data = await request.receive()
        body = data.get("body")
        if not body:
            return Response(404, b"")
        if f"{uu}.article" not in os.listdir(self.getpath("editor/sessions")):
            return Response(404, b"Cannot find the article")
        async with aiofiles.open(self.getpath(f"editor/sessions/{uu}.article"), "wb") as stream:
            await stream.write(body)

        try:
            generator.generate_single(
                self.getpath(f"editor/sessions/{uu}.article"),
                self.getpath(f"editor/html"),
                raise_errors=True,
                render_template=self.factory.jinja_env.get_template("index.html").render,
                render_mobile=True
            )
        except generator.GenerationError as e:
            return Response(500, str(e.args[0]).encode())

        return Response(200, b"Updated!")

    @regex_path(r"/editor/([^/]+)/edit$")
    async def handler_editor_edit(self, request: Request, uu: str):
        if f"{uu}.article" not in os.listdir(self.getpath("editor/sessions")):
            return Response(404, b"Cannot find the article")
        async with aiofiles.open(self.getpath(f"editor/sessions/{uu}.article"), "r") as stream:
            contents = await stream.read()
        return self.factory.form("editor.html", {"uu": uu, "contents": contents})

    @regex_path(r"/editor/([^/]+)$")
    @resolve_mobile
    async def handler_editor_article(self, request: Request, uu: str, mobile: bool):
        if f"{uu}.article" not in os.listdir(self.getpath("editor/sessions")):
            return Response(404, "Undefined")
        return ArticleResponse(self.editor_factory, f"{uu}", self.getpath("editor/html"), mobile)

    @regex_path(r"/editor$")
    async def handler_edit_new(self, request: Request):
        uu = uuid.uuid4().hex
        async with aiofiles.open(self.getpath(f"editor/sessions/{uu}.article"), "w") as stream:
            await stream.write(self.editor_default_contents)
        generator.generate_single(
            self.getpath(f"editor/sessions/{uu}.article"),
            self.getpath(f"editor/html"),
            raise_errors=True,
            render_template=self.factory.jinja_env.get_template("index.html").render,
            render_mobile=True
        )
        return self.factory.form("redirect.html", {"url": f"/editor/{uu}/edit"})

    async def undefined(self, request: Request) -> ABCResponse:
        return self.factory.form("redirect.html", {"url": "/"})


if __name__ == "__main__":
    print("wiki should be ran with actor")
