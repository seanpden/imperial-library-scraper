from bs4 import BeautifulSoup
from scrape_book_info import construct_soup
import polars as pl


def find_author(text_block, ret: dict):
    try:
        author = text_block.find(class_="field field-type-text field-field-author")
        ret.get("author", None).append(author.text)
        return author
    except AttributeError:
        ret.get("author", None).append(None)
        return None


def find_comment(text_block, ret: dict):
    try:
        comment = text_block.find(class_="field field-type-text field-field-comment")
        ret.get("comment", None).append(comment.text)
    except AttributeError:
        ret.get("comment", None).append(None)


def find_text(main_div, ret: dict):
    try:
        text = main_div.find(class_="node-content clear-block prose")
        ret.get("text", None).append(text.text)
        return text
    except AttributeError:
        ret.get("text", None).append(None)
        return None


def construct_book_content(soup: BeautifulSoup):
    ret = {"author": [], "comment": [], "text": []}

    main_div = soup.find(id="main", class_="clear-block")
    text_block = find_text(main_div, ret)

    find_author(text_block, ret)
    find_comment(text_block, ret)

    return ret


def iter_over_links(df: pl.DataFrame, restrict=None):
    ltc = ""
    loop = df.height if restrict else 1

    ret = {
        "link_to_content": [],
        "author": [],
        "comment": [],
        "text": [],
    }

    for i in range(loop):
        ltc = str(df[i, "link_to_content"])
        soup = construct_soup(ltc)

        book_content = construct_book_content(soup)
        author = book_content.get("author", list())[0]
        comment = book_content.get("comment", list())[0]
        text = book_content.get("text", list())[0]

        ret.get("link_to_content", list()).append(ltc)
        ret.get("author", list()).append(author)
        ret.get("comment", list()).append(comment)
        ret.get("text", list()).append(text)

    return ret


def handle_df(ret: dict):
    df = pl.DataFrame(ret)
    df = df.filter(~pl.all_horizontal(pl.col(["author", "comment", "text"]).is_null()))
    return df
