import os
import jinja2
import json
from generator import generate_single

ARTICLES_FOLDER = "docs/articles"

with open("config.json") as config_file:
    config = json.load(config_file)

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(["templates"]))
jinja_env.globals["config"] = config

article_template = jinja_env.get_template("index.html")


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
        print(
            "\033[F["
            + ("*" * i)
            + (" " * (len(path_list) - i))
            + "] Generating "
            + new_path
            + " " * 20
        )
        generate_single(
            ARTICLES_FOLDER + os.sep + article,
            "html", render_template=article_template.render,
            render_mobile=True
        )

    print("\033[F[" + ("*" * len(path_list)) + "] Generation completed." + " " * 64)


if __name__ == "__main__":
    generate()
