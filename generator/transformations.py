import re


def extra_transformations(article: str) -> str:
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
