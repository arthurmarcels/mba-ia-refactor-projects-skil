"""Report and category routes — endpoint definitions delegating to controllers."""
from flask import Blueprint, request, jsonify
from controllers.report_controller import ReportController, CategoryController
from middlewares.auth import token_required

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
@token_required
def summary_report(current_user_id):
    result = ReportController.get_summary()
    return jsonify(result), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
@token_required
def user_report(current_user_id, user_id):
    result, status = ReportController.get_user_report(user_id)
    return jsonify(result), status


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    result = CategoryController.get_all()
    return jsonify(result), 200


@report_bp.route('/categories', methods=['POST'])
@token_required
def create_category(current_user_id):
    data = request.get_json()
    result, status = CategoryController.create(data)
    return jsonify(result), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@token_required
def update_category(current_user_id, cat_id):
    data = request.get_json()
    result, status = CategoryController.update(cat_id, data)
    return jsonify(result), status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@token_required
def delete_category(current_user_id, cat_id):
    result, status = CategoryController.delete(cat_id)
    return jsonify(result), status
