import logging

logger = logging.getLogger(__name__)


def send_order_created(pedido_id, usuario_id):
    logger.info(
        "notification.order_created pedido_id=%s usuario_id=%s",
        pedido_id,
        usuario_id,
    )


def send_status_changed(pedido_id, status):
    logger.info(
        "notification.order_status_changed pedido_id=%s status=%s",
        pedido_id,
        status,
    )
