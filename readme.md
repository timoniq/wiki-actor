# wiki

Minimalistic wiki built with [actor](https://github.com/timoniq/actor).

(c) timoniq, 2022

## how to set up

## setting up uvicorn-actor

Install poetry (`pip3 install poetry`) and then actor environment:

```shell
git clone https://github.com/timoniq/actor.git
```

Then enter `actor` directory (you can rename it if you wish) and configure poetry:

```shell
cd actor
poetry install
poetry shell
```

## setting up wiki actor

Install wiki into actor environment directory:

```shell
git clone https://github.com/timoniq/wiki-actor.git
```

Add address alias pointing to `wiki-actor` (in `ADDRESSES`), like this:

```
127.0.0.1:8080 -> wiki-actor
```

Enter the directory:

```shell
cd wiki-actor
```

After preparing articles and revising `config.json` run

```
python3 generate.py
```

to turn articles into static htmls.

Then go back to `actor` directory and run `main.py` or use `uvicorn` cli.