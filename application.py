from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Book, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random
import string
import json
import requests
import httplib2


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Catalog"

engine = create_engine('sqlite:///bookcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' "style = "width: 300px; height: 300px;
                 border-radius: 150px;
                 -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Show login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


#JSON endpoints
@app.route('/categories/<category_name>/JSON')
def categoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    books = session.query(Book).filter_by(category_id=category.id).all()
    return jsonify(books=[i.serialize for i in books])


@app.route('/categories/<category_name>/<int:book_id>/JSON')
def bookJSON(category_name, book_id):
    category = session.query(Category).filter_by(name=category_name).one()
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=book.serialize)


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(list=[i.serialize for i in categories])


# Show home page
@app.route('/')
@app.route('/home')
def homePage():
    TODO = "Categories + Most viewed / trending section"
    categories = session.query(Category)
    return render_template('index.html', categories=categories)


# Show category page
@app.route('/categories/<category_name>')
def categoryPage(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    books = session.query(Book).filter_by(category_id=category.id)
    return render_template('category.html', category=category, books=books,
                           category_name=category_name)


# Show book page
@app.route('/categories/<category_name>/<int:book_id>',
           methods=['GET', 'POST'])
def bookPage(category_name, book_id):
    category = session.query(Category).filter_by(name=category_name).one()
    books = session.query(Book).filter_by(category_id=category.id)
    book = session.query(Book).filter_by(id=book_id).one()
    return render_template('book.html', book=book, books=books,
                           category=category, category_name=category_name)


# Create new book in selected category
@app.route('/categories/<category_name>/new/', methods=['GET', 'POST'])
def newBook(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        newBook = Book(
            title=request.form['title'],
            author=request.form['author'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            category=category
            )
        session.add(newBook)
        session.commit()
        flash("New book added.")
        return redirect(url_for('categoryPage', category_name=category_name))
    else:
        return render_template("newbook.html", category_name=category_name)


# Edit book
@app.route('/categories/<category_name>/<int:book_id>/edit/',
           methods=['GET', 'POST'])
def editBook(category_name, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedBook = session.query(Book).filter_by(id=book_id).one()
    if editedBook.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert(
               'You are not authorized to edit this item.'
               );}</script><body onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['title']:
            editedBook.title = request.form['title']
        if request.form['author']:
            editedBook.author = request.form['author']
        if request.form['description']:
            editedBook.description = request.form['description']
        session.add(editedBook)
        session.commit()
        flash("Book edited.")
        return redirect(url_for('categoryPage', category_name=category_name))
    else:
        return render_template(
            'editbook.html', category_name=category_name, book_id=book_id,
            book=editedBook)


# Delete book
@app.route('/categories/<category_name>/<int:book_id>/delete/',
           methods=['GET', 'POST'])
def deleteBook(category_name, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookToDelete = session.query(Book).filter_by(id=book_id).one()
    if bookToDelete.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert(
               'You are not authorized to delete this item.'
               );}</script><body onload='myFunction()'>"""
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash("Book deleted.")
        return redirect(url_for('categoryPage', category_name=category_name))
    else:
        return render_template('deletebook.html', category_name=category_name,
                               book=bookToDelete)


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
