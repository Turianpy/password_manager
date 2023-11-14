from celery import shared_task
from celery.utils.log import get_task_logger

from .utils import generate_user_token, send_activation_email

logger = get_task_logger(__name__)


@shared_task(name='send_activation_email')
def send_activation_email_task(data):
    username, email = data['username'], data['email']
    token = generate_user_token(email)
    logger.info(f'Sending activation email to {username} at {email}')
    send_activation_email(username, email, token)
    return 1
