from flask import Flask, jsonify, make_response, request
from entities import users

app = Flask(__name__)


@app.route('/users/createUser', methods=['POST'])
def create_user():
    payload = request.json
    return users.create(payload)
    

@app.route("/users/getUserById/<string:user_id>", methods=['GET'])
def get_user(user_id):
    return users.get(user_id)


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
