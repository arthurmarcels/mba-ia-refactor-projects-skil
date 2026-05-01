"""Task routes — endpoint definitions delegating to TaskController."""
from flask import Blueprint, request, jsonify
from controllers.task_controller import TaskController
from middlewares.auth import token_required

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    result = TaskController.get_all_tasks()
    return jsonify(result), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    result, status = TaskController.get_task_by_id(task_id)
    return jsonify(result), status


@task_bp.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user_id):
    data = request.get_json()
    result, status = TaskController.create_task(data)
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user_id, task_id):
    data = request.get_json()
    result, status = TaskController.update_task(task_id, data)
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user_id, task_id):
    result, status = TaskController.delete_task(task_id)
    return jsonify(result), status


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')
    result = TaskController.search_tasks(query, status, priority, user_id)
    return jsonify(result), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    result = TaskController.get_stats()
    return jsonify(result), 200
