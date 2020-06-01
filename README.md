Web Programming with Python and JavaScript

#Project 1

Description –  Users will be able to register for your website and then log in using their username and password. Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. The website also uses a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users will be able to query for book details and book reviews programmatically via your website’s API.

The project meets all the requirements that were provided apart from that users will also
be able to edit and delete their reviews.

#Templates-
Login.html - The screen contains the login form consists of a username and password.

register.html - The screen contains an input field to sign up for a new user. A new user can register by entering a name, username, and password.

search.html - The search screen contains the input for ISBN, Title, and Author. The user can enter either one of them or all of them. The search will provide the result even if part of ISBN, Title, and Author were entered.

serachbook.html - This screen is the output of the search performed by the user. It displays a list of possible matching results. The user can click on the title of the books to know more detail about the book.

book_detail.html - The screen contains the details about the book like Author, Title, ISBN, Total Ratings(good reads), Average Rating(good reads) and reviews given by users. On this page, the user will get the option to edit and delete his review. User is not allowed to submit multiple reviews for the same book.

editReview.html - The screen will allow the user to edit the review.

layout.html - This file contains the common code (Navigation bar) for all pages.

#static/stylesheet/styles.css
- contains the styling for the web application.

#applicatipn.py
- A flask file that contains all the routes and API calls.

#import.py  
- take the books contained in books.csv and import them into the PostgreSQL database.

# API access -
Users can make a get request to the website (/api/isbn route). The website will return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.  

The web application uses bootstrap for most of the styling.
