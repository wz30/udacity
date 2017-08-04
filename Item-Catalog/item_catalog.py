import json
import httplib2
import requests
import string
import random
import os
from flask import Flask, url_for, session, redirect, request, render_template
from flask import jsonify, make_response, send_from_directory
from item_database_config import Item
from database_operations import DatabaseOperations
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from werkzeug import secure_filename


app = Flask(__name__)


db = DatabaseOperations()
credentials = {}
token_info = {}

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'PNG'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Static Pages
@app.route('/')
@app.route('/category/')
def showCategories():
    createSession()
    categories = db.getListOfCategories()
    latestItems = db.getLatestItems()
    return render_template('category_list.html',
                           categories=categories,
                           items=latestItems,
                           user_id=session.get('user_id'),
                           STATE=session.get('state'))


@app.route('/category/<int:category_id>/')
def showItemsForCategory(category_id):
    createSession()
    categories = db.getListOfCategories()
    category = db.getCategoryBy(category_id)
    items = db.getItemsFor(category_id)
    return render_template('category.html',
                           main_category=category,
                           categories=categories,
                           items=items,
                           user_id=session.get('user_id'),
                           STATE=session.get('state'))


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    createSession()
    categories = db.getListOfCategories()
    item = db.getItemBy(item_id)
    print uploaded_file(item[0].image_url)
    return render_template('item.html',
                           categories=categories,
                           item=item,
                           main_category=category_id,
                           user_id=session.get('user_id'),
                           STATE=session.get('state'))


# Send uploadedfiles.
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# CRUD Operations
@app.route('/category/<int:category_id>/addItem', methods=['GET', 'POST'])
def addItemToCategory(category_id):
    if 'name' not in session:
        return redirect(url_for('showCategories'))

    else:
        category = db.getCategoryBy(category_id)
        if request.method == 'POST':
            if checkIfClientAuthorizedWith(request.form['state']) is False:
                return responseWith('Invalid authorization paramaters.', 401)
            #print 'Trying to upload file.'
			#return redirect(url_for('showItemsForCategory', category_id=category.id))
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print 'Trying to save file'
		#print app.config['UPLOAD_FOLDER']
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print 'File upload complete'
                new_item = Item(name=request.form['name'],
                                image_url=filename,
                                description=request.form['description'],
                                category_id=category.id,
                                creator_id=session['user_id'])
                db.addToDatabase(new_item)

                return redirect(url_for('showItemsForCategory', category_id=category.id))

            else:
                return responseWith('Bad image.', 422)
        else:
            return render_template('addItem.html',
                                   category=category,
                                   STATE=session.get('state'))


@app.route('/category/<int:category_id>/editItem/<int:item_id>/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'name' not in session:
        return redirect(url_for('showCategories'))

    item_to_edit = db.getItemBy(item_id)

    if request.method == 'POST':
        if checkIfClientAuthorizedWith(request.form['state']) is False:
            return responseWith('Invalid authorization paramaters.', 401)

        if request.form['name']:
            item_to_edit[0].name = request.form['name']

        if request.form['description']:
            item_to_edit[0].description = request.form['description']
        print 'Checking to see if we have a new file.'
        if request.files['file']:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item_to_edit[0].image_url = filename
            else:
                return responseWith('Bad Image', 422)

        db.addToDatabase(item_to_edit[0])

        return redirect(url_for('showItem',
                                category_id=item_to_edit[1].id,
                                item_id=item_to_edit[0].id,
                                STATE=session.get('state')))
    else:
        return render_template('editItem.html',
                               category=item_to_edit[1],
                               item=item_to_edit[0],
                               STATE=session.get('state'))


@app.route('/category/<int:category_id>/deleteItem/<int:item_id>/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'name' not in session:
        return redirect(url_for('showCategories'))

    item_to_delete = db.getItemBy(item_id)

    if request.method == 'POST':
        if checkIfClientAuthorizedWith(request.form['state']) is False:
            return responseWith('Invalid authorization paramaters.', 401)

        db.deleteFromDatabase(item_to_delete[0])

        return redirect(url_for('showItemsForCategory',
                                category_id=item_to_delete[1].id))
    else:
        return render_template('deleteItem.html',
                               category=item_to_delete[1],
                               item=item_to_delete[0],
                               STATE=session.get('state'))


#Connect and Disconnect endpoints.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    return checkIfAuthorizedWith(request)


@app.route('/gdisconnect')
def gdisconnect():
    return logout()


# JSON API
@app.route('/categories/JSON/')
def categoriesJSON():
    categories = db.getListOfCategories()
    return jsonify(categories=[category.serialize for category in categories])


@app.route('/category/<int:category_id>/items/JSON/')
def itemsJSON(category_id):
    items = db.getItemsFor(category_id)
    return jsonify(items=[item.serialize for item in items])


# oAuth Flow and Error Checking
def checkIfClientAuthorizedWith(client_state):
    return client_state == session['state']


def checkIfAuthorizedWith(client_request):
    if not checkIfClientAuthorizedWith(client_request.args.get('state')):
        return responseWith('Invalid authentication paramaters.', 401)
    else:
        request_data = client_request.data
        return tryOAuthFlow(request_data)


def tryOAuthFlow(request_data):
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        setCredentials(oauth_flow.step2_exchange(request_data))
        return validateAccess()
    except FlowExchangeError:
        return responseWith('Failed to upgrade the authorization code.', 401)


def validateAccess():
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % credentials.access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        return responseWith(result.get('error'), 500)
    else:
        setTokenInfo(result)
    return checkIfTokenInfoAndCrednetialForSameUser()


def checkIfTokenInfoAndCrednetialForSameUser():
    if token_info['user_id'] != credentials.id_token['sub']:
        return responseWith('Token\'s user ID doesn\'t match given user ID.', 401)
    else:
        return checkIfTokenIssuedToClient()


def checkIfTokenIssuedToClient():
    if token_info['issued_to'] != CLIENT_ID:
        return responseWith('Token\'s client ID does not match.', 401)
    else:
        return checkIfUserLoggedIn()


def checkIfUserLoggedIn():
    if session.get('credentials') is not None:
        if credentials.id_token['sub'] == session.get('gplus_id'):
            return responseWith('Current user is already connected.', 200)
    else:
        return getUserInfoAndCreateSession()


def getUserInfoAndCreateSession():
    url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    response = requests.get(url, params=params)
    data = response.json()
    session['access_token'] = credentials.access_token
    session['gplus_id'] = credentials.id_token['sub']
    session['name'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    session['user_id'] = db.getUserBy(session).id
    print session.get('access_token')
    return responseWith('User successfully connected.', 200)


def logout():
    if session.get('access_token')is None:
        return responseWith('Current user not connected', 401)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session.get('access_token')
    h = httplib2.Http()
    print 'In gdisconnect access token is %s', session.get('access_token')
    print 'User name is: '
    print session['name']
    result = h.request(url, 'GET')[0]
    print session
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['name']
        del session['picture']
        del session['email']
        del session['user_id']
        return redirect(url_for('showCategories'))
    else:
        return responseWith('Failed to revoke token for given user.', 400)


# Setters for global variables
def setCredentials(new_credential):
    global credentials
    credentials = new_credential


def setTokenInfo(token):
    global token_info
    token_info = token


#Utility Methods
def allowed_file(filename):
    if '..' in filename or filename.startswith('/'):
        return False
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def createSession():
    if session.get('state') is None:
        session['state'] = ''.join(random.choice(string.ascii_uppercase + string.digits)
                           for x in xrange(32))


def responseWith(message, response_code):
    response = make_response(json.dumps(message), response_code)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
