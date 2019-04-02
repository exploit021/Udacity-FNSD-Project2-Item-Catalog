#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Udacity Full Stack Web Developer Nanodegree
# Project 2: Item Catalog
# Author: Youngseo Kim
# Date: 4/1/2019

from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

GOOGLE_CLIENT_ID = json.loads(
    open('google_client_secrets.json', 'r').read())['web']['client_id']
FACEBOOK_CLIENT_ID = json.loads(
    open('facebook_client_secrets.json', 'r').read())['web']['app_id']
APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine(
    'sqlite:///itemcatalog.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Login with Facebook Account
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print ("access token received %s " % access_token)

    app_id = json.loads(
        open('facebook_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('facebook_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token? \
            grant_type=fb_exchange_token&client_id=%s&client_secret=%s \
            &fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server
        token exchange we have to split the token first on commas
        and select the first index which gives us the key : value
        for the server access token then we split it on colons
        to pull out the actual token value and replace the remaining
        quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s \
            &fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s \
            &redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
            150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output


# Logout with Facebook Account
# - Revoke a current user's token and reset their login_session
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Login with Google Account
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
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json',
                                             scope='')
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
    if result['issued_to'] != GOOGLE_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

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
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px; \
            -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    return output


# Logout with Facebook Account
# - Revoke a current user's token and reset their login_session
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
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Logout based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('showCategories'))
    else:
        return redirect(url_for('showCategories'))


# Create user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get user information
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Get user ID
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    # except NoResultFound:
    #     return None
    # except MultipleResultsFound:
    #     return None
    except:
        return None


# Show all catalogs
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latestItems = session.query(Item).order_by(desc(Item.id)).limit(10).all()
    return render_template(
        'categories.html', categories=categories, latestItems=latestItems)


# Create a category
@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)

        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


# Edit a category
@app.route(
    '/catalog/category/<int:category_id>/edit/',
    methods=['GET', 'POST'])
def editCategory(category_id):
    categoryToEdit = session.query(
        Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You\
            are not authorized to edit this category.\
            Please create your own category in order\
            to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']

            return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('editCategory.html', category=categoryToEdit)


# Delete a category
@app.route(
    '/catalog/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You\
            are not authorized to delete this category.\
            Please create your own category in order\
            to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(categoryToDelete)

        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'deleteCategory.html', category=categoryToDelete)


# Show all items for a category
@app.route('/catalog/category/<int:category_id>/items/')
def showCategory(category_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = next(
        iter([
            category for category in categories
            if category.id == category_id] or []
        ), None)
    if category is None:
        return render_template('notfound.html'), 404
    items = session.query(Item).filter_by(
        category_id=category_id).order_by(Item.name).all()
    return render_template(
        'category.html',
        categories=categories,
        category=category,
        items=items)


# Show a item
@app.route('/catalog/item/<int:item_id>/')
def showItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item=item)


# Create an item
@app.route(
    '/catalog/category/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category_id,
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()

        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('newitem.html', category=category)


# Edit an item
@app.route('/catalog/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You\
         are not authorized to edit this item.\
          Please create your own item in order\
           to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        request_category_id = -1
        try:
            request_category_id = int(request.form['category'])
        except ValueError:
            return create_json_error_response(
                "Invalid category_id: {}".format(
                    request.form['category']), 400)
        if request_category_id not in \
                [category.id for category in categories]:
            return create_json_error_response(
                "category_id does not exist: {}".format(
                    request_category_id), 409)
        item.category_id = request_category_id
        session.add(item)
        session.commit()

        return redirect(url_for('showCategory', category_id=item.category_id))
    else:
        return render_template(
            'edititem.html', item=item, categories=categories)


# Delete an item
@app.route('/catalog/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You\
            are not authorized to delete this item.\
            Please create your own item in order\
            to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showCategory', category_id=item.category_id))
    else:
        return render_template('deleteitem.html', item=item)


# JSON APIs to view a category
@app.route('/api/catalog/categories/<int:category_id>/')
def getCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category=category.serialize)


# JSON APIs to view item
@app.route('/api/catalog/items/<int:item_id>/')
def getItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


# JSON APIs to view categories
@app.route('/api/catalog/categories/')
def getCategories():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


if __name__ == '__main__':
    app.secret_key = FACEBOOK_CLIENT_ID
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
