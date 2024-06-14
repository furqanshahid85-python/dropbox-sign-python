from dropbox_sign import models
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmbeddedSignatureRequest(db.Model):
    """Model for storing EmbeddedSignatureRequest obj"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sigid = db.Column(db.String(120), nullable=False)


class DropboxModel:
    """Model class for Dropbox Sign API"""

    def __init__(self) -> None:
        pass

    def set_signer(self, name, email):
        """set the document signers here"""
        return models.SubSignatureRequestSigner(
            email_address=email,
            name=name,
            order=0,
        )

    def set_signing_option(self):
        """sets the document signing options"""
        return models.SubSigningOptions(
            draw=True,
            type=True,
            upload=True,
            phone=True,
            default_type="draw",
        )

    def set_data(self, client_id, signers_list, file_path, signing_options):
        """creates the data object sent with the signing request"""
        return models.SignatureRequestCreateEmbeddedRequest(
            client_id=client_id,
            title="NDA with Acme Co.",
            subject="The NDA we talked about",
            message="Please sign this NDA and then we can discuss more. Let me know if you have any questions.",
            signers=signers_list,  # [signer_1, signer_2],
            files=[open(file_path, "rb")],
            # file_urls=["https://app.hellosign.com/docs/example_signature_request.pdf"],
            signing_options=signing_options,
            test_mode=True,
        )
