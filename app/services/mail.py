#!/usr/bin/env python3
"""send user recovery email"""

import logging
from app.extensions import mail
from app.models.v2 import User
from flask_mail import Message
from flask import render_template
from celery import shared_task


@shared_task(bind=True)
def send_password_reset_email(self, data):
    logger = logging.getLogger(__name__)
    user_id = data.get('user_id')
    password = data.get('password')
    email = data.get('email')
    user = User.query.get(user_id)
    if user:
        msg = Message(
            subject="Password Reset Request",
            sender="bonnyrangi95@gmail.com",
            recipients=[email]
        )
        msg.html = render_template(
            'forgot_password.html',
            username=user.username, password=password
            )
        try:
            mail.send(msg)
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
    else:
        logger.error("User not found with ID: %s" % user_id)
