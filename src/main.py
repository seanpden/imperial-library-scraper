import scrape_book_info as sbi
import scrape_book_contents as sbc

URL = "https://www.imperial-library.info/books/all/by-category"


def main():
    """Main entry"""
    soup = sbi.construct_soup(URL)  # Create base soup object

    # Book info
    ret = sbi.construct_ret(soup)
    df = sbi.handle_df(ret)
    print(df.head(n=1))

    # TODO: Clean strings...
    # Book contents
    new_ret = sbc.iter_over_links(df)
    new_df = sbc.handle_df(new_ret)
    print(new_df)


if __name__ == "__main__":
    main()
