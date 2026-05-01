"""Centralized error handling middleware for Flask."""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': str(e.description) if hasattr(e, 'description') else str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({'error': str(e.description) if hasattr(e, 'description') else str(e)}), 409

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f'Internal error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f'Unhandled exception: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
