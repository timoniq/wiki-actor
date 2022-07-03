import os
import re
import typing

SUBARTICLE = re.compile(r"\.article$")

getpath: typing.Callable[[str], str]


def all_articles() -> typing.Iterable[typing.Tuple[str, str]]:
    articles = [
        a for a in os.listdir(getpath("docs/articles")) if a.islower() and not a.startswith("_")
    ]

    return sorted(
        [
            (
                open(getpath("docs/articles/" + a), "r").readline(),
                re.sub(SUBARTICLE, "", a).replace("__", "/"),
            )
            for a in articles
        ],
        key=lambda e: e[0].lower(),
    )


snippet_funcs = {
    "get_articles": all_articles,
}
