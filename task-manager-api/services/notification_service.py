"""Notification service — email notifications for task events."""
import smtplib
import logging
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(Config.SMTP_USER, to, message)
            server.quit()
            logger.info(f'Email enviado para {to}')
            return True
        except Exception as e:
            logger.error(f'Erro ao enviar email: {e}')
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\n"
            f"Status: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': datetime.utcnow()
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
