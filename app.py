import os

from dotenv import load_dotenv
from dropbox_sign import ApiClient, Configuration, apis
from flask import Flask, render_template, request, jsonify

from backend.models import DropboxModel, EmbeddedSignatureRequest, db


# Load environment variables from .env file
load_dotenv()

# setup flask app
app = Flask(__name__)

# Configuring the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dropbox.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the SQLAlchemy object with the Flask app
db.init_app(app)

# Create the database and the tables
with app.app_context():
    db.create_all()

# Access environment variables
app.config["API_KEY"] = os.getenv("API_KEY")
app.config["CLIENT_ID"] = os.getenv("CLIENT_ID")


# Setup dropbox credentials using Configuration class
configuration = Configuration(
    # Configure HTTP basic authorization: api_key
    username=app.config.get("API_KEY")
)

# initialize the dropbox API clients

api_client = ApiClient(configuration)
# api_client = DropboxClient(config=configuration)
signature_request_api = apis.SignatureRequestApi(api_client)
embeded_api = apis.EmbeddedApi(api_client)
model_obj = DropboxModel()


# app routes
@app.route("/")
def home():
    """default route"""
    # return render_template(f"{project_dir}/templates/home.html")
    return render_template("home.html")


@app.route("/admin_view")
def admin_view():
    """admin page route"""
    return render_template("admin.html")


@app.route("/user_view")
def user_view():
    """user page route"""
    return render_template("user.html")


@app.route("/generate_singing_url", methods=["POST"])
def generate_singing_url():
    """Gets user information and creates signing URL."""
    name = request.form.get("name")
    email = request.form.get("email")
    document = request.form.get("document")
    print(
        f"Received signature request for document: {document} and user: {name}, {email}"
    )

    signer = model_obj.set_signer(name=name, email=email)

    siging_options = model_obj.set_signing_option()
    req_data = model_obj.set_data(
        client_id=app.config.get("CLIENT_ID"),
        signers_list=[signer],
        file_path=document,
        signing_options=siging_options,
    )
    print(app.config.get("CLIENT_ID"))
    response = signature_request_api.signature_request_create_embedded(req_data)
    for sig_req in response["signature_request"]["signatures"]:
        signature_request_name = sig_req["signer_name"]
        signature_request_id = sig_req["signature_id"]
        new_req = EmbeddedSignatureRequest(
            name=signature_request_name, sigid=signature_request_id
        )
        db.session.add(new_req)
        db.session.commit()

    return "<h1> Document Signature Request created</h1>"


@app.route("/sign_document")
def sign_document():
    """Creates sign url and send to frontend for signature by user"""
    sig_req = EmbeddedSignatureRequest.query.filter_by(name="jack").first()
    sign_url = embeded_api.embedded_sign_url(sig_req.sigid)["embedded"]["sign_url"]
    return jsonify({"clientid": app.config.get("CLIENT_ID"), "signurl": sign_url})


if __name__ == "__main__":
    app.run(debug=True)
