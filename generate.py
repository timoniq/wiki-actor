import re
import os
import markdown2
import jinja2
import dataclasses
import typing
import json

ARTICLES_FOLDER = "docs/articles"
SEPARATOR = "*---*"

with open("config.json") as config_file:
    config = json.load(config_file)

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(["templates"]))
jinja_env.globals["config"] = config

article_template = jinja_env.get_template("index.html")


@dataclasses.dataclass
class Article:
    title: str
    tags: typing.List[str]
    preambula: str
    contents: str
    data: typing.Dict[str, str]


def extra_tranformations(article: str) -> str:
    article = re.sub(
        r"\[(.*?)]{(.*?)}\((.*?)\)", r'<a href="\3" title="\2">\1</a>', article
    )
    article = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", article)
    article = re.sub(
        r"^# (.+)$",
        r'<h1 class="article"><span>\1</span> <a name="\1" href="#\1">🔗</a></h1>',
        article,
        flags=re.MULTILINE,
    )
    article = re.sub(
        r"!\[(.+)]\((.+)\)",
        r'<div class="img"><img src="\2" onclick="open_img(this)"><p>\1</p></div>',
        article,
    )
    code_snippets = re.findall(r"```.*?```", article, flags=re.MULTILINE | re.DOTALL)

    for old_snip in code_snippets:
        snip = "\\n".join(old_snip.split("\n"))
        snip = re.sub(
            r"```(.*?)```",
            r'<pre class="prettyprint" translate="no">\1</pre>',
            snip.replace("<", "&lt").replace(">", "&gt"),
        )
        article = article.replace(old_snip, snip, 1)

    snips = re.findall(r"`(.*?)`", article, flags=re.MULTILINE)
    for snip in snips:
        nsnip = snip
        for ch in "\\_*":
            nsnip = nsnip.replace(ch, "\\" + ch)
        article = article.replace(
            "`" + snip + "`", "<span class=code translate='no'>{}</span>".format(nsnip)
        )
    article = re.sub(r"([^\n])\n", r"\1 ", article).replace("\\n", "\n")
    return article


def render_contents(article: str) -> str:
    article = extra_tranformations(article)
    return markdown2.markdown(article)


def generate():
    print("Generating static htmls from articles...\n")

    if not os.path.exists("html"):
        os.mkdir("html")
    else:
        for p in os.listdir("html"):
            os.remove("html" + os.sep + p)

    path_list = os.listdir(ARTICLES_FOLDER)
    for i, article in enumerate(path_list):
        new_path = "html" + os.sep + article.replace(".article", ".html")
        new_path_mobile = (
            "html" + os.sep + "mobile:" + article.replace(".article", ".html")
        )
        print(
            "\033[F["
            + ("*" * (i))
            + (" " * (len(path_list) - i))
            + "] Generating "
            + new_path
            + " " * 20
        )
        with open(ARTICLES_FOLDER + os.sep + article, "r") as stream:
            data = stream.read()
            parts = data.split(SEPARATOR)
            if len(parts) != 3:
                print(
                    f"{article} was not loaded: "
                    f"Article should consist of header, preambula and contents splitted by {SEPARATOR} separator\n"
                )
                continue

            header, preambula, contents = parts
            title, *opt = header.splitlines()
            tags = []
            data = {}
            if opt:
                tags = list(map(str.strip, opt.pop(0).split(",")))
                data = dict(tuple(s.split("=")) for s in opt)

            article = Article(
                title=title,
                tags=tags,
                preambula=render_contents(preambula),
                contents=render_contents(contents),
                data=data,
            )
            with open(new_path, "w") as file:
                file.write(article_template.render(article=article))
            with open(new_path_mobile, "w") as file:
                file.write(article_template.render(article=article, mobile=True))

    print("\033[F[" + ("*" * len(path_list)) + "] Generation completed." + " " * 64)


if __name__ == "__main__":
    print("start")
    generate()
