from actor import Response, HTMLResponseFactory, HTMLResponse
import typing
import dataclasses
import os


@dataclasses.dataclass
class Article:
    title: str
    tags: typing.List[str]
    preambula: str
    contents: str
    data: typing.Dict[str, str]


class ArticleResponse(Response):
    def __init__(
        self,
        factory: HTMLResponseFactory,
        article_name: str,
        html_path: str,
        mobile: bool = False,
    ):
        if "/" in article_name:
            spl = article_name.split("/")
            if len(spl) > 2:
                self.status_code = 404
                self.body = b""
                return
            article_name = "__".join(spl)

        article_name = article_name.replace(" ", "_")

        full_name = article_name + ".html"
        if full_name not in os.listdir(html_path):
            super().__init__(200, b"")
            r = factory.form(
                "index.html",
                {"article": Article("Undefined", [], "", "", {}), "mobile": mobile},
            )
            self.body = r.body
            self.status_code = r.status_code
            self.content_type = r.content_type
            return

        with open(html_path + os.sep + ("mobile:" if mobile else "") + full_name) as file:
            body = file.read()
        super().__init__(200, body)
        self.content_type = "text/html"


def gen_search_response(
    factory: HTMLResponseFactory,
    search: str,
    found_articles: typing.List[typing.Tuple[str, str]],
    mobile: bool = False,
) -> HTMLResponse:
    return factory.form(
        "index.html",
        dict(
            article={
                "title": f"Search results for «{search.lower().capitalize()}»",
                "preambula": "",
                "contents": (
                    "\n".join(
                        [
                            "<ol>",
                            *[
                                f'<li><a href="/wiki/{a[0]}">{a[1]}</a></li>'
                                for a in found_articles
                            ],
                            "</ol>",
                        ]
                    )
                    if len(found_articles)
                    else "Nothing found"
                ),
            },
            mobile=mobile,
        ),
    )
