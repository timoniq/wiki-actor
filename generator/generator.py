import dataclasses
import generator.transformations
import markdown2
import typing
import os

SEPARATOR = "*---*"


@dataclasses.dataclass
class Article:
    title: str
    tags: typing.List[str]
    preambula: str
    contents: str
    data: typing.Dict[str, str]


def render_contents(article: str) -> str:
    article = generator.transformations.extra_transformations(article)
    return markdown2.markdown(article)


class GenerationError(Exception):
    pass


def generate_single(
        article_file_path: str,
        html_file_directory: str,
        raise_errors: bool = False,
        render_template: typing.Optional[typing.Callable] = None,
        render_mobile: bool = True
):
    article_filename = article_file_path.split(os.sep)[-1]
    with open(article_file_path, "r") as stream:
        data = stream.read()
        parts: typing.List[str] = data.split(SEPARATOR)
        if len(parts) != 3:
            msg = f"found {len(parts) - 1} separators, must be 3"
            if raise_errors:
                raise GenerationError(msg)
            print(msg)
            return
        header, preambula, contents = parts
        title, *options = header.splitlines()
        tags = []
        data = {}
        if options:
            tags = list(map(str.strip, options.pop(0).split(",")))
            data = dict(tuple(s.split("=")) for s in options)

        article = Article(
            title,
            tags,
            render_contents(preambula),
            render_contents(contents),
            data
        )

        html_filename = article_filename.replace(".article", ".html")
        html_data = render_template(article=article)
        with open(html_file_directory + os.sep + html_filename, "w") as new_stream:
            new_stream.write(html_data)

        if render_mobile:
            html_data = render_template(article=article, mobile=True)
            with open(html_file_directory + os.sep + "mobile:" + html_filename, "w") as new_stream:
                new_stream.write(html_data)
