import scrape_book_info as sbi
import scrape_book_contents as sbc

URL = "https://www.imperial-library.info/books/all/by-category"


def main():
    """Main entry"""
    soup = sbi.construct_soup(URL)
    ret = sbi.construct_ret(soup)
    df = sbi.handle_df(ret)
    sbc.foo(df)


if __name__ == "__main__":
    main()
