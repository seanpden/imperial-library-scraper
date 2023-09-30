import requests
from bs4 import BeautifulSoup
import polars as pl


BASE_URL = "https://www.imperial-library.info"


def construct_soup(URL: str) -> BeautifulSoup:
    """Constructs a BeautifulSoup object with the URL provided - using html.parser.

    Args:
        URL (str): a valid URL as a string
    Returns:
        soup (BeautifulSoup): A soup object
    """
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


def find_titles(li, ret: dict) -> str | None:
    """Parses a list item and appends the title that exists there to a dict.

    Args:
        li (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'title' key with a list as values
    Returns:
        title (str): the title as a string
    """
    try:
        title = li.find(class_="views-field views-field-title").text
        ret.get("title", None).append(title)
        return title
    except AttributeError:
        ret.get("title", None).append(None)
        return None


def find_link_to_content(li, ret) -> str | None:
    """Parses a list item and appends the link to content that exists there to a dict.

    Args:
        li (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'link_to_content' key with a list as values
    Returns:
        link_to_content (str): the link_to_content as a string
    """

    try:
        link_to_content = ""
        for href in li.find_all("a"):
            link_to_content = href.get("href")  # Only 1 href per li
        ret.get("link_to_content").append(f"{BASE_URL}{link_to_content}")
        return link_to_content
    except AttributeError:
        ret.get("link_to_content").append(None)
        return None


def find_author(li, ret):
    """Parses a list item and appends the author that exists there to a dict.

    Args:
        li (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'author' key with a list as values
    Returns:
        author (str): the author as a string
    """
    try:
        author = li.find(class_="views-field views-field-field-author-value").text
        ret.get("author").append(author)
        return author
    except AttributeError:
        ret.get("author").append(None)
        return None


def find_summary(li, ret: dict) -> str | None:
    """Parses a list item and appends the summary that exists there to a dict.

    Args:
        li (PageElement): A page element of a BS4 ResultSet[Any]
        ret (dict): A dictionary including a 'summary' key with a list as values
    Returns:
        summary (str): the summary as a string
    """
    try:
        summary = li.find(class_="views-field views-field-field-summary-value").text
        ret.get("summary", None).append(summary)
        return summary
    except AttributeError:
        ret.get("summary", None).append(None)
        return None


def construct_ret(soup: BeautifulSoup) -> dict:
    """Finds title, link_to_content, author, summary and returns a dict with that info.

    Parses the soup object with helper functions and constructs a dict with
    the author, title, link to book, and summary of book.

    Args:
        soup (BeautifulSoup): BeautifulSoup object with imperial library data

    Returns:
        ret (dict): dict formatted for book info
    """
    ret = {"title": [], "link_to_content": [], "author": [], "summary": []}

    results = soup.find_all("li")
    # Iterates over all list items in html - they act as blocks with book info
    for li in results:
        find_titles(li, ret)
        find_link_to_content(li, ret)
        find_author(li, ret)
        find_summary(li, ret)

    return ret


def handle_df(ret: dict) -> pl.DataFrame:
    """Handles formatting the book info into a polars DF.

    Args:
        ret (dict): a dict of book info
    Returns:
        df (pl.DataFrame): A polars dataframe of the book info dict

    """
    df = pl.DataFrame(ret)
    df = df.filter(~pl.all_horizontal(pl.col(["title", "author", "summary"]).is_null()))
    return df
