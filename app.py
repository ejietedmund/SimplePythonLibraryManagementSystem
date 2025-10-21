from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# -------------------------
# Simple configuration
# -------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Lockvault@25#',        
    'database': 'librarydb'
}

app = Flask(__name__)
app.secret_key = 'dev-secret-key'  # for flash messages; change for production


# -------------------------
# Helper: get database connection
# -------------------------
def get_db_connection():
    """
    Return a new MySQL connection using mysql-connector-python.
    Use parameterized queries to avoid SQL injection.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        return conn
    except Error as e:
        # In a real app, log this error. We'll raise it so Flask shows it during development.
        raise e


# -------------------------
# Home page: links to sections
# -------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------
# BOOKS: List, Add, Edit, Delete, Search
# -------------------------
@app.route('/books')
def books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Books ORDER BY BookID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('books.html', books=rows)


@app.route('/books/add', methods=['POST'])
def add_book():
    # Insert book record
    title = request.form.get('title')
    author = request.form.get('author')
    category = request.form.get('category')
    copies = request.form.get('copies') or 1

    if not title or not author:
        flash('Title and author are required.', 'error')
        return redirect(url_for('books'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Books (Title, Author, Category, Copies) VALUES (%s, %s, %s, %s)",
            (title, author, category, int(copies))
        )
        conn.commit()
        flash('Book added successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding book: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('books'))


@app.route('/books/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    # Update book record
    title = request.form.get('title')
    author = request.form.get('author')
    category = request.form.get('category')
    copies = request.form.get('copies') or 1

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Books SET Title=%s, Author=%s, Category=%s, Copies=%s WHERE BookID=%s",
            (title, author, category, int(copies), book_id)
        )
        conn.commit()
        flash('Book updated successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating book: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('books'))


@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Books WHERE BookID=%s", (book_id,))
        conn.commit()
        flash('Book deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting book: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('books'))


@app.route('/books/search')
def search_books():
    q = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Books WHERE Title LIKE %s OR Author LIKE %s OR Category LIKE %s",
        (f'%{q}%', f'%{q}%', f'%{q}%')
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # return JSON so frontend can render without page reload if desired
    return jsonify(rows)


# -------------------------
# MEMBERS: List, Add, Edit, Delete, Search
# -------------------------
@app.route('/members')
def members():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Members ORDER BY MemberID DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('members.html', members=rows)


@app.route('/members/add', methods=['POST'])
def add_member():
    name = request.form.get('name')
    contact = request.form.get('contact')
    if not name:
        flash('Name is required.', 'error')
        return redirect(url_for('members'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Members (Name, Contact) VALUES (%s, %s)", (name, contact))
        conn.commit()
        flash('Member added successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error adding member: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('members'))


@app.route('/members/update/<int:member_id>', methods=['POST'])
def update_member(member_id):
    name = request.form.get('name')
    contact = request.form.get('contact')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Members SET Name=%s, Contact=%s WHERE MemberID=%s", (name, contact, member_id))
        conn.commit()
        flash('Member updated.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating member: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('members'))


@app.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Members WHERE MemberID=%s", (member_id,))
        conn.commit()
        flash('Member deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting member: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('members'))


@app.route('/members/search')
def search_members():
    q = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Members WHERE Name LIKE %s OR Contact LIKE %s", (f'%{q}%', f'%{q}%'))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------
# BORROWINGS: List, Add, Edit(return), Delete, Search
# -------------------------
@app.route('/borrowings')
def borrowings():
    # Show borrowings with joined member and book info
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.BorrowID, b.MemberID, b.BookID, b.BorrowDate, b.ReturnDate,
               m.Name AS MemberName, bk.Title AS BookTitle
        FROM Borrowings b
        LEFT JOIN Members m ON b.MemberID = m.MemberID
        LEFT JOIN Books bk ON b.BookID = bk.BookID
        ORDER BY b.BorrowID DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Also prepare lists of members and books for the 'add' form
    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT MemberID, Name FROM Members ORDER BY Name")
    members = c.fetchall()
    c.execute("SELECT BookID, Title, Copies FROM Books ORDER BY Title")
    books = c.fetchall()
    c.close()
    conn.close()

    return render_template('borrowings.html', borrowings=rows, members=members, books=books)


@app.route('/borrowings/add', methods=['POST'])
def add_borrowing():
    member_id = request.form.get('member_id')
    book_id = request.form.get('book_id')
    borrow_date = request.form.get('borrow_date') or datetime.today().strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Simple check: does the book exist and are copies available?
        cursor.execute("SELECT Copies FROM Books WHERE BookID=%s", (book_id,))
        row = cursor.fetchone()
        if not row:
            flash('Book not found.', 'error')
            return redirect(url_for('borrowings'))
        copies = row[0]
        if copies < 1:
            flash('No copies available.', 'error')
            return redirect(url_for('borrowings'))

        # Insert borrowing
        cursor.execute(
            "INSERT INTO Borrowings (MemberID, BookID, BorrowDate) VALUES (%s, %s, %s)",
            (member_id, book_id, borrow_date)
        )
        # reduce copies by 1
        cursor.execute("UPDATE Books SET Copies = Copies - 1 WHERE BookID=%s", (book_id,))
        conn.commit()
        flash('Borrowing recorded.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error recording borrowing: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('borrowings'))


@app.route('/borrowings/return/<int:borrow_id>', methods=['POST'])
def return_book(borrow_id):
    return_date = request.form.get('return_date') or datetime.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Find the borrowing to get the BookID
        cursor.execute("SELECT BookID FROM Borrowings WHERE BorrowID=%s", (borrow_id,))
        row = cursor.fetchone()
        if not row:
            flash('Borrowing not found.', 'error')
            return redirect(url_for('borrowings'))
        book_id = row[0]

        # Set return date
        cursor.execute("UPDATE Borrowings SET ReturnDate=%s WHERE BorrowID=%s", (return_date, borrow_id))
        # increase copies by 1
        cursor.execute("UPDATE Books SET Copies = Copies + 1 WHERE BookID=%s", (book_id,))
        conn.commit()
        flash('Book returned successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error returning book: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('borrowings'))


@app.route('/borrowings/delete/<int:borrow_id>', methods=['POST'])
def delete_borrowing(borrow_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Borrowings WHERE BorrowID=%s", (borrow_id,))
        conn.commit()
        flash('Borrowing record deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting borrowing: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('borrowings'))


@app.route('/borrowings/search')
def search_borrowings():
    q = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # search member name or book title
    cursor.execute("""
        SELECT b.BorrowID, b.MemberID, b.BookID, b.BorrowDate, b.ReturnDate,
               m.Name AS MemberName, bk.Title AS BookTitle
        FROM Borrowings b
        LEFT JOIN Members m ON b.MemberID = m.MemberID
        LEFT JOIN Books bk ON b.BookID = bk.BookID
        WHERE m.Name LIKE %s OR bk.Title LIKE %s
    """, (f'%{q}%', f'%{q}%'))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------
# Run the app
# -------------------------
if __name__ == '__main__':
    # Use debug=True for development; turn off in production
    app.run(debug=True, host='0.0.0.0', port=5000)
