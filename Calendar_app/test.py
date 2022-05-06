import pathlib
#from secrets import token_urlsafe
from flask import Flask, abort, redirect, request, session
from google_auth_oauthlib.flow import Flow
import os
import pip._vendor.cachecontrol
import google
import google.oauth2.id_token

app = Flask("Google Login App")
app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "808118809457-212igj3jc37i6gcql2u87btgvdg1rore.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "credentials.json")
 
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes = [ "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"], 
    redirect_uri="http://127.0.0.1:5000/callback"
                                    )

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    #flow.fetch_token(authorization_response=request.url)
    # if not session["state"] == request.args["state"]:
    #     abort(500)

    #credentials = flow.credentials
    #print("credentials\n",credentials)
    # request_session = request.session()
    # cached_session = pip._vendor.cachecontrol.CacheControl(request_session)
    # token_request = google.auth.transport.Request(session=cached_session)

    # id_info = google.oauth2.id_token.verify_oauth2_token(
    #     id_token = credentials._id_token,
    #     request=token_request,
    #     audience=GOOGLE_CLIENT_ID
    # )
    # print (id_info )
    return "fuck you"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def index():
    return "hello world <a href ='login'><button>login</button></a>"

@app.route("/protected_area")
@login_is_required
def protected_area():
    return "Protected!<a href ='logout'><button>logout</button></a>"

if __name__ == "__main__":
    app.run(debug=True)