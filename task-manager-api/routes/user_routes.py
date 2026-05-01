"""User routes — endpoint definitions delegating to UserController."""
from flask import Blueprint, request, jsonify
from controllers.user_controller import UserController
from middlewares.auth import token_required

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user_id):
    result = UserController.get_all_users()
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    result, status = UserController.get_user_by_id(user_id)
    return jsonify(result), status


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    result, status = UserController.create_user(data)
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user_id, user_id):
    data = request.get_json()
    result, status = UserController.update_user(user_id, data)
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user_id, user_id):
    result, status = UserController.delete_user(user_id)
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
@token_required
def get_user_tasks(current_user_id, user_id):
    result, status = UserController.get_user_tasks(user_id)
    return jsonify(result), status


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result, status = UserController.login(data)
    return jsonify(result), status
