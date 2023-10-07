from bs4 import BeautifulSoup
from scrape_book_info import construct_soup
import polars as pl


def print_progress(current, total):
    print(f"{((current/total)*100):.2f}%")


def find_author(text_block, ret: dict) -> str | None:
    """Parses a text_block and appends the author that exists there to a dict.

    Args:
        text_block (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'author' key with a list as values
    Returns:
        author (str): the author as a string
    """
    try:
        author = text_block.find(class_="field field-type-text field-field-author")
        author_text = process_author(author)
        ret.get("author", None).append(author_text)
        return author
    except AttributeError:
        ret.get("author", None).append(None)
        return None


def process_author(author) -> str:
    """Processes the author text and formats it appropriately

    Args:
        author (PageElement): a page element of author info
    Returns:
        author (str): the author as a string
    """
    author_text = author.text.strip().splitlines()
    author_text = [ele.strip() for ele in author_text]
    author_text = author_text[1:]
    author_text = " ".join(author_text)

    return author_text


def find_comment(text_block, ret: dict) -> str | None:
    """Parses a text block and appends the comment that exists there to a dict.

    Args:
        text_block (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'comment' key with a list as values
    Returns:
        author (str): the author as a string
    """
    try:
        comment = text_block.find(class_="field field-type-text field-field-comment")
        comment_text = process_comment(comment)
        ret.get("comment", None).append(comment_text)
        return comment
    except AttributeError:
        ret.get("comment", None).append(None)
        return None


def process_comment(comment) -> str:
    """Processes the comment text and formats it appropriately

    Args:
        comment (PageElement): a page element of comment info
    Returns:
        comment (str): the comment as a string
    """
    comment_text = comment.text.strip().splitlines()
    comment_text = [ele.strip() for ele in comment_text]
    comment_text = comment_text[1:]
    comment_text = "\n".join(comment_text)
    return comment_text


def find_text(main_div, ret: dict) -> str | None:
    """Parses a div and appends the main text block that exists there to a dict.

    Args:
        main_div (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'text' key with a list as values
    Returns:
        author (str): the author as a string
    """
    try:
        text = main_div.find(class_="node-content clear-block prose")
        text_text = process_text(text)
        ret.get("text", None).append(text_text)
        return text
    except AttributeError:
        ret.get("text", None).append(None)
        return None


def process_text(text) -> str:
    """Processes the author text and formats it appropriately

    Args:
        author (PageElement): a page element of author info
    Returns:
        author (str): the author as a string
    """
    text_text = text.text.strip()
    return text_text


def construct_book_content(soup: BeautifulSoup) -> dict:
    """Finds author, comment, and text and returns a dict with that info.

    Args:
        soup (BeautifulSoup): BeautifulSoup object with imperial library data

    Returns:
        ret (dict): dict formatted for book contents
    """
    ret = {"author": [], "comment": [], "text": []}

    main_div = soup.find(id="main", class_="clear-block")
    text_block = find_text(main_div, ret)

    find_author(text_block, ret)
    find_comment(text_block, ret)

    return ret


def iter_over_links(df: pl.DataFrame) -> dict:
    """Iterates over a dataframe, then produces a dict of book info from df.

    DF must have 'link_to_content' column, with valid links to the Imperial Library.

    Args:
        df (pl.DataFrame): A polars dataframe.
        restrict (bool): whether or not to restrict the iteration to just one value.
    Returns:
        ret (dict): A dictionary of link_to_content, author, comment, and text values.
    """
    ltc = ""
    loop = df.height

    ret = {
        "link_to_content": [],
        "author": [],
        "comment": [],
        "text": [],
    }

    for i in range(loop):
        print(f"Progress: {((i/loop) * 100):.2f}%")
        print_progress(i, loop)
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


def handle_df(ret: dict) -> pl.DataFrame:
    """Handles formatting the book content into a polars DF.

    Args:
        ret (dict): a dict of book content
    Returns:
        df (pl.DataFrame): A polars dataframe of the book content dict

    """
    df = pl.DataFrame(ret)
    df = df.filter(~pl.all_horizontal(pl.col(["author", "comment", "text"]).is_null()))
    return df
