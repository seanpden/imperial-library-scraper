import requests
from bs4 import BeautifulSoup
from scrape_book_info import construct_soup
import polars as pl


def foo(df: pl.DataFrame):
    for i in range(3):
        ltc = str(df[i, "link_to_content"])
        soup = construct_soup(ltc)
        stuff = soup.find_all(class_="node-content clear-block prose")
        for ele in stuff:
            print(ele.text)
    return ltc
