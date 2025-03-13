'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file, response,redirect,abort
from secrets import token_bytes as random
import model
from sql import SQLDatabase
import json
sec = random(30)
#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login/register page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

@get('/register')
def get_register_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.register_form()
#-----------------------------------------------------------------------------

# Attempt the login/register
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    # Call the appropriate method
    ifTrue, body = model.login_check(username, password)
    if ifTrue:
        response.set_cookie("id",username,secret=sec)
        return body
    else:
        return body



@post('/register')
def post_register():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    iv = request.forms.get('iv')
    aes_prikey = request.forms.get('aes_prikey')
    pubkey = request.forms.get('pubkey')
    
    # Call the appropriate method
    return model.register_check(username, password,iv,aes_prikey,pubkey)

#-----------------------------------------------------------------------------
# Display the message page
@get('/message')
def get_message():
    '''
        get_message
        
        Serves the message page
    '''
    username=request.get_cookie("id",secret=sec)
    if username is None:
        return redirect("/login")
    return model.message()

#-----------------------------------------------------------------------------
# ask for the public key of the user for sending message
@post('/message')
def get_pub_key():
    aim_user = request.forms.get("aim_user")
    key = SQLDatabase.running.getPubKey(aim_user)
    if key == False:
        abort(404)
    return key
#-----------------------------------------------------------------------------
# ask for the encrypted private key of current user
@post('/get_private_key')
def get_pri_key():
    username = request.get_cookie("id",secret=sec)
    password  = request.forms.get("password")
    key = SQLDatabase.running.getPrivateKey(username,password)
    if key == False:
        abort(404)
    chipter,iv = key
    return json.dumps({"chipter":chipter,"iv":iv})
#-----------------------------------------------------------------------------
# redirect to mesage page
@get('/send_msg')
def get_send_msg():
    return redirect("/message")
#-----------------------------------------------------------------------------
# Users send message to server
@post('/send_msg')
def post_send_msg():
    '''
        Handles send message attempts
    '''
    input = request.forms.get("input")
    aim = request.forms.get("aim")
    username=request.get_cookie("id",secret=sec)
    if not SQLDatabase.check_exists(username,aim):
        abort(400)
    SQLDatabase.running.add_msg(input,username,aim)
    response.set_cookie("success","True")
    return model.post_message(request.forms.get('input'),request.forms.get('aim'))

#-----------------------------------------------------------------------------
# Users fetch message from server
@get('/check_message')
def post_message():
    '''
        Handles get message attempts
    '''
    username=request.get_cookie("id",secret=sec)
    if not SQLDatabase.check_exists(username):
        abort(400)
    l = SQLDatabase.running.get_msg(username)
    if l[0] == 0:
        response.status = 204
        return ""
    l[0] = str(l[0])
    f = open("outerr","a")
    f.write(str(l)+"\n")
    f.close()
    return "".join(l)    

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
