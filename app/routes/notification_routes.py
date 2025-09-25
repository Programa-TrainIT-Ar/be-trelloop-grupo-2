from flask import Blueprint
from flask_jwt_extended import jwt_required
from flasgger.utils import swag_from
from ..controllers.notification_controller import get_notifications, mark_notification_as_read, test_create_notification

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

@notification_bp.route('', methods=['GET'])
@jwt_required()
@swag_from('../swagger_docs/notifications/get_notification.yaml')
def handle_get_notifications():
    return get_notifications()

@notification_bp.route('/<int:notification_id>', methods=['POST'])
@jwt_required()
@swag_from('../swagger_docs/notifications/mark_notification_as_read.yaml')
def handle_mark_notification_as_read(notification_id):
    return mark_notification_as_read(notification_id)

@notification_bp.route('/test_create', methods=['POST'])
@jwt_required()
@swag_from('../swagger_docs/notifications/test_create_notification.yaml')
def handle_test_create_notification():
    return test_create_notification()