from flask import Blueprint, jsonify

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})
