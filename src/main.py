import scrape_book_info as sbi
import scrape_book_contents as sbc
import database


URL = "https://www.imperial-library.info/books/all/by-category"


def main():
    """Main entry"""
    soup = sbi.construct_soup(URL)  # Create base soup object

    # Book info
    print("Getting book info...")
    book_info = sbi.construct_ret(soup)
    book_info_df = sbi.handle_df(book_info)

    # Book contents
    # TODO: Clean book text...
    print("Getting book contents...")
    book_content = sbc.iter_over_links(book_info_df)
    book_content_df = sbc.handle_df(book_content)

    # store in DB table
    # store book_info
    print("Storing book info...")
    book_info_df.write_database(
        table_name="book_info",
        connection=database.CNXN_STR,
        if_exists="replace",
        engine=database.ENGINE,
    )

    # store book_content
    print("Storing book contents...")
    book_content_df.write_database(
        table_name="book_content",
        connection=database.CNXN_STR,
        if_exists="replace",
        engine=database.ENGINE,
    )


if __name__ == "__main__":
    main()
