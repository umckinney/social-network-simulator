from pathlib import Path

from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from social_network.main import reconcile_images, initialize_db

app = Flask(__name__, instance_path=str(Path("../320-sp25-assignment-10-umckinney-main").absolute()))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///socialnetwork.db"
db = SQLAlchemy(app)
api = Api(app)


class UserRecord(db.Model):
    """
    Creating our user model
    """

    __tablename__ = "UserTable"
    id = db.Column(db.Integer)
    user_id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    user_name = db.Column(db.String)
    user_last_name = db.Column(db.String)

    def serialize(self):
        """
        Helper method to generate json
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email,
            "user_name": self.user_name,
            "user_last_name": self.user_last_name,
        }


class StatusRecord(db.Model):
    """
    Creating our status model
    """

    __tablename__ = "StatusTable"
    id = db.Column(db.Integer)
    status_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String)
    status_text = db.Column(db.String)

    def serialize(self):
        """
        Helper method to generate json
        """
        return {
            "id": self.id,
            "status_id": self.status_id,
            "user_id": self.user_id,
            "status_text": self.status_text,
        }


class PictureRecord(db.Model):
    """
    Creating our picture model
    """

    __tablename__ = "PictureTable"
    id = db.Column(db.Integer)
    picture_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String)
    tags = db.Column(db.String)
    file_name = db.Column(db.String)

    def serialize(self):
        """
        Helper method to generate json
        """
        return {
            "id": self.id,
            "picture_id": self.picture_id,
            "user_id": self.user_id,
            "tags": self.tags,
            "file_name": self.file_name,
        }


class Index(Resource):
    def get(self):
        html = """
        <html>
            <head><title>API Index</title></head>
            <body>
                <h1>Implemented APIs (top level)</h1>
                <ul>
                    <li><a href="/users">/users</a></li>
                    <ul>
                        <li>Leave bare to see all records.</li>
                        <li>Append "/&ltuser_id&gt" to see individual records</li>
                    </ul>
                    <li><a href="/statuses">/statuses</a></li>
                    <ul>
                        <li>Leave bare to see all records.</li>
                        <li>Append "/&ltstatus_id&gt" to see individual records</li>
                    </ul>
                    <li><a href="/images">/images</a></li>
                    <ul>
                        <li>Leave bare to see all records.</li>
                        <li>Append "/&ltpicture_id&gt" to see individual records</li>
                    </ul>
                    <li><a href="/differences">/differences</a></li>
                    <ul>
                        <li>Leave bare to see all records.</li>
                        <li>Append "?user_id=&ltuser_id&gt" to see individual records</li>
                    </ul>
                </ul>
            </body>
        </html>
        """
        return make_response(html, 200)


class Users(Resource):
    """
    Returns a JSON list of all user records from the database.
    """

    def get(self):
        return jsonify([record.serialize() for record in UserRecord.query.all()])


class Statuses(Resource):
    """
    Returns a JSON list of all status records from the database.
    """

    def get(self):
        return jsonify([record.serialize() for record in StatusRecord.query.all()])


class Pictures(Resource):
    """
    Returns a JSON list of all picture records from the database.
    """

    def get(self):
        return jsonify([record.serialize() for record in PictureRecord.query.all()])


class BaseLookupByUID(Resource):
    """
    Base class for getting records by a unique ID value
    Returns a JSON list of all records matching the query parameters from the database.
    """

    model = None
    uid_field = None

    def get(self, **kwargs):
        if not self.model or not self.uid_field:
            return {"error": "model and uid_field must be defined"}, 500

        uid = kwargs.get(self.uid_field)
        if not uid:
            return {"error": "uid field must be provided in the URL"}, 400

        record = self.model.query.filter_by(**{self.uid_field: uid}).first_or_404(
            description=f"Could not find record in {self.model.__name__} where {self.uid_field}={uid}"
        )
        return jsonify(record.serialize())


class LookupUserByID(BaseLookupByUID):
    """
    Returns a JSON list of all user records matching the user_id value from the database.
    """

    model = UserRecord
    uid_field = "user_id"


class LookupStatusByID(BaseLookupByUID):
    """
    Returns a JSON list of all status records matching the status_id value from the database.
    """

    model = StatusRecord
    uid_field = "status_id"


class LookupPictureByID(BaseLookupByUID):
    """
    Returns a JSON list of all picture records matching the picture_id value from the database.
    """

    model = PictureRecord
    uid_field = "picture_id"


class LookupUnReconciledImages(Resource):
    """
    Returns a JSON dictionary of reconciliation results comparing the database and file system.

    If a 'user_id' query parameter is provided, only that user's images are checked.
    If no 'user_id' is provided, all users are checked.

    Example:
        GET /differences?user_id=some_user_id
    """

    def get(self):
        user_id = request.args.get("user_id")

        user_table, _, picture_table = initialize_db()

        results = reconcile_images(user_table, picture_table, user_id=user_id)

        return jsonify(results)


api.add_resource(Index, "/", endpoint="index")
api.add_resource(Users, "/users", endpoint="users")
api.add_resource(LookupUserByID, "/users/<user_id>", endpoint="lookupuserbyid")
api.add_resource(Statuses, "/statuses", endpoint="statuses")
api.add_resource(LookupStatusByID, "/statuses/<status_id>", endpoint="lookupstatusbyid")
api.add_resource(Pictures, "/images", endpoint="pictures")
api.add_resource(
    LookupPictureByID, "/images/<picture_id>", endpoint="lookuppicturebyid"
)
api.add_resource(
    LookupUnReconciledImages, "/differences", endpoint="lookupunreconciledimages"
)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
