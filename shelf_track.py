"""
shelf_track.py

Capstone Project - Databases
A bookstore inventory management program ("Shelf Track") that allows a
clerk to add, update, delete and search for books, as well as view a
combined report of every book together with its author's details.

The program uses an SQLite database (ebookstore.db) with two tables:
    book    -> id, title, authorID, qty
    author  -> id, name, country

Run this file directly to launch the interactive menu:
    python3 shelf_track.py
"""

import sqlite3
from contextlib import closing

DATABASE_NAME = "ebookstore.db"

# ---------------------------------------------------------------------------
# Seed data used to populate the database the first time it is created.
# ---------------------------------------------------------------------------
INITIAL_BOOKS = [
    (3001, "A Tale of Two Cities", 1290, 30),
    (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
    (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
    (3004, "The Lord of the Rings", 6380, 37),
    (3005, "Alice's Adventures in Wonderland", 5620, 12),
]

INITIAL_AUTHORS = [
    (1290, "Charles Dickens", "England"),
    (8937, "J.K. Rowling", "England"),
    (2356, "C.S. Lewis", "Ireland"),
    (6380, "J.R.R. Tolkien", "South Africa"),
    (5620, "Lewis Carroll", "England"),
]


# ---------------------------------------------------------------------------
# Database setup helpers
# ---------------------------------------------------------------------------
def create_tables(cursor):
    """Create the book and author tables if they do not already exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS author (
            id      INTEGER PRIMARY KEY,
            name    TEXT NOT NULL,
            country TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS book (
            id       INTEGER PRIMARY KEY,
            title    TEXT NOT NULL,
            authorID INTEGER NOT NULL,
            qty      INTEGER NOT NULL,
            FOREIGN KEY (authorID) REFERENCES author (id)
        )
        """
    )


def populate_tables(cursor):
    """Populate the tables with the starter data set (only if empty)."""
    cursor.execute("SELECT COUNT(*) FROM author")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
            INITIAL_AUTHORS,
        )

    cursor.execute("SELECT COUNT(*) FROM book")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)",
            INITIAL_BOOKS,
        )


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def is_valid_four_digit_id(value):
    """Return True if value is a string of exactly 4 digits (an integer ID)."""
    return value.isdigit() and len(value) == 4


def prompt_for_id(prompt_text):
    """Repeatedly prompt the user until a valid 4-digit integer ID is entered.

    Returns None if the user types 'q' to cancel the operation.
    """
    while True:
        value = input(prompt_text).strip()
        if value.lower() == "q":
            return None
        if is_valid_four_digit_id(value):
            return int(value)
        print("Invalid ID. Please enter exactly four digits (or 'q' to cancel).")


def prompt_for_positive_int(prompt_text):
    """Repeatedly prompt until a valid non-negative integer quantity is entered."""
    while True:
        value = input(prompt_text).strip()
        if value.lower() == "q":
            return None
        if value.isdigit():
            return int(value)
        print("Invalid quantity. Please enter a whole number (or 'q' to cancel).")


def prompt_for_non_empty_text(prompt_text):
    """Repeatedly prompt until non-empty text is entered."""
    while True:
        value = input(prompt_text).strip()
        if value.lower() == "q":
            return None
        if value:
            return value
        print("This field cannot be empty. Please try again (or 'q' to cancel).")


# ---------------------------------------------------------------------------
# Core functionality
# ---------------------------------------------------------------------------
def enter_book(cursor, connection):
    """Add a new book to the book table, prompting for an author if needed."""
    print("\n-- Enter a new book --  (type 'q' at any prompt to cancel)")

    book_id = prompt_for_id("Book ID (4 digits): ")
    if book_id is None:
        print("Cancelled.")
        return

    cursor.execute("SELECT 1 FROM book WHERE id = ?", (book_id,))
    if cursor.fetchone():
        print(f"A book with ID {book_id} already exists.")
        return

    title = prompt_for_non_empty_text("Title: ")
    if title is None:
        print("Cancelled.")
        return

    author_id = prompt_for_id("Author ID (4 digits): ")
    if author_id is None:
        print("Cancelled.")
        return

    cursor.execute("SELECT name, country FROM author WHERE id = ?", (author_id,))
    author = cursor.fetchone()
    if author is None:
        print("That author ID does not exist yet. Let's add the author first.")
        author_name = prompt_for_non_empty_text("Author's name: ")
        author_country = prompt_for_non_empty_text("Author's country: ")
        if author_name is None or author_country is None:
            print("Cancelled.")
            return
        try:
            cursor.execute(
                "INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
                (author_id, author_name, author_country),
            )
        except sqlite3.Error as error:
            print(f"Database error while adding author: {error}")
            return

    qty = prompt_for_positive_int("Quantity: ")
    if qty is None:
        print("Cancelled.")
        return

    try:
        cursor.execute(
            "INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)",
            (book_id, title, author_id, qty),
        )
        connection.commit()
        print(f"Book '{title}' added successfully.")
    except sqlite3.Error as error:
        print(f"Database error while adding book: {error}")


def _get_book(cursor, book_id):
    """Return a single book row (id, title, authorID, qty) or None."""
    cursor.execute(
        "SELECT id, title, authorID, qty FROM book WHERE id = ?", (book_id,)
    )
    return cursor.fetchone()


def update_book(cursor, connection):
    """Update a book's quantity, title or author link, or the linked
    author's own name/country."""
    print("\n-- Update a book --  (type 'q' at any prompt to cancel)")

    book_id = prompt_for_id("Enter the ID of the book to update: ")
    if book_id is None:
        print("Cancelled.")
        return

    book = _get_book(cursor, book_id)
    if book is None:
        print(f"No book found with ID {book_id}.")
        return

    _, title, author_id, qty = book
    cursor.execute("SELECT name, country FROM author WHERE id = ?", (author_id,))
    author = cursor.fetchone()
    author_name, author_country = author if author else ("Unknown", "Unknown")

    print(f"\nCurrent details for book {book_id}:")
    print(f"  Title:            {title}")
    print(f"  Quantity:         {qty}")
    print(f"  Author's Name:    {author_name}")
    print(f"  Author's Country: {author_country}")

    print("\nWhat would you like to update?")
    print("1. Quantity (default)")
    print("2. Title")
    print("3. Author ID (link this book to a different author)")
    print("4. This author's name and/or country")
    choice = input("Select an option [1-4, default 1]: ").strip() or "1"

    try:
        if choice == "1":
            new_qty = prompt_for_positive_int("New quantity: ")
            if new_qty is None:
                print("Cancelled.")
                return
            cursor.execute(
                "UPDATE book SET qty = ? WHERE id = ?", (new_qty, book_id)
            )

        elif choice == "2":
            new_title = prompt_for_non_empty_text("New title: ")
            if new_title is None:
                print("Cancelled.")
                return
            cursor.execute(
                "UPDATE book SET title = ? WHERE id = ?", (new_title, book_id)
            )

        elif choice == "3":
            new_author_id = prompt_for_id("New author ID (4 digits): ")
            if new_author_id is None:
                print("Cancelled.")
                return
            cursor.execute("SELECT 1 FROM author WHERE id = ?", (new_author_id,))
            if not cursor.fetchone():
                print(f"No author exists with ID {new_author_id}. Update aborted.")
                return
            cursor.execute(
                "UPDATE book SET authorID = ? WHERE id = ?",
                (new_author_id, book_id),
            )

        elif choice == "4":
            new_name = input(
                f"New author name (leave blank to keep '{author_name}'): "
            ).strip()
            new_country = input(
                f"New author country (leave blank to keep '{author_country}'): "
            ).strip()
            new_name = new_name or author_name
            new_country = new_country or author_country
            cursor.execute(
                "UPDATE author SET name = ?, country = ? WHERE id = ?",
                (new_name, new_country, author_id),
            )

        else:
            print("Invalid option selected. No changes made.")
            return

        connection.commit()
        print("Update saved successfully.")

    except sqlite3.Error as error:
        print(f"Database error while updating: {error}")


def delete_book(cursor, connection):
    """Delete a book from the book table by ID."""
    print("\n-- Delete a book --  (type 'q' to cancel)")

    book_id = prompt_for_id("Enter the ID of the book to delete: ")
    if book_id is None:
        print("Cancelled.")
        return

    book = _get_book(cursor, book_id)
    if book is None:
        print(f"No book found with ID {book_id}.")
        return

    confirm = input(f"Delete '{book[1]}' (ID {book_id})? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    try:
        cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
        connection.commit()
        print("Book deleted successfully.")
    except sqlite3.Error as error:
        print(f"Database error while deleting: {error}")


def search_books(cursor):
    """Search for books by ID or by a (partial) title match."""
    print("\n-- Search books --")
    print("1. Search by ID")
    print("2. Search by title")
    choice = input("Select an option [1-2]: ").strip()

    if choice == "1":
        book_id = prompt_for_id("Enter book ID (4 digits): ")
        if book_id is None:
            print("Cancelled.")
            return
        cursor.execute(
            """
            SELECT book.id, book.title, book.qty, author.name, author.country
            FROM book
            INNER JOIN author ON book.authorID = author.id
            WHERE book.id = ?
            """,
            (book_id,),
        )
    elif choice == "2":
        keyword = prompt_for_non_empty_text("Enter a title or part of a title: ")
        if keyword is None:
            print("Cancelled.")
            return
        cursor.execute(
            """
            SELECT book.id, book.title, book.qty, author.name, author.country
            FROM book
            INNER JOIN author ON book.authorID = author.id
            WHERE book.title LIKE ?
            """,
            (f"%{keyword}%",),
        )
    else:
        print("Invalid option.")
        return

    results = cursor.fetchall()
    if not results:
        print("No matching books found.")
        return

    print(f"\nFound {len(results)} result(s):")
    print("-" * 50)
    for book_id, title, qty, author_name, author_country in results:
        print(f"ID: {book_id}")
        print(f"Title: {title}")
        print(f"Quantity: {qty}")
        print(f"Author's Name: {author_name}")
        print(f"Author's Country: {author_country}")
        print("-" * 50)


def view_all_books(cursor):
    """Display title, author name and author country for every book,
    joining the book and author tables on authorID."""
    cursor.execute(
        """
        SELECT book.title, author.name, author.country
        FROM book
        INNER JOIN author ON book.authorID = author.id
        ORDER BY book.id
        """
    )
    rows = cursor.fetchall()

    if not rows:
        print("\nNo books in the database.")
        return

    print("\nDetails")
    print("-" * 50)
    for title, author_name, author_country in rows:
        print(f"Title: {title}")
        print(f"Author's Name: {author_name}")
        print(f"Author's Country: {author_country}")
        print("-" * 50)


# ---------------------------------------------------------------------------
# Menu / main program loop
# ---------------------------------------------------------------------------
MENU_TEXT = """
Shelf Track - Bookstore Menu
1. Enter book
2. Update book
3. Delete book
4. Search books
5. View details of all books
0. Exit
"""


def run_menu(cursor, connection):
    """Display the menu and dispatch to the appropriate function until
    the user chooses to exit."""
    actions = {
        "1": lambda: enter_book(cursor, connection),
        "2": lambda: update_book(cursor, connection),
        "3": lambda: delete_book(cursor, connection),
        "4": lambda: search_books(cursor),
        "5": lambda: view_all_books(cursor),
    }

    while True:
        print(MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid option. Please choose a number from the menu.")
            continue

        try:
            action()
        except sqlite3.Error as error:
            print(f"An unexpected database error occurred: {error}")


def main():
    """Entry point: open the database, ensure it is set up, and run the menu."""
    try:
        with closing(sqlite3.connect(DATABASE_NAME)) as connection:
            with closing(connection.cursor()) as cursor:
                create_tables(cursor)
                populate_tables(cursor)
                connection.commit()
                run_menu(cursor, connection)
    except sqlite3.Error as error:
        print(f"Could not open the database: {error}")


if __name__ == "__main__":
    main()
