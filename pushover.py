import os
import requests

from dotenv import load_dotenv
from logger import logger

class Pushover:
    
    HEADERS = {'Content-Type': 'application/json'}
    PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'

    def __init__(self, user, app_token, log_token, app_name):
        load_dotenv()

        self.user = user
        self.app_token = app_token
        self.log_token = log_token
        self.app_name = app_name

        if not self.user or not self.app_token or not self.log_token:
            logger.error("One or more required environment variables are missing.")
            raise ValueError("Missing environment variables for Pushover configuration.")

    def send_notification(self, msg, priority=0, is_log=False, monospace=0):
        """
        Make an API call to Pushover.

        Args:
            msg (str): The message text to be sent via Pushover.
            priority (int): Notification priority, as defined by the Pushover API specification.
            is_log (bool): If True, the notification is sent to the Logs project using PUSHOVER_LOG_TOKEN.
                Otherwise, it is logged to the app project using PUSHOVER_APP_TOKEN.
            monospace (enum [0, 1]): Enum options based on Pushover API docs. 
                If 1, the text is monospaced. Defaults to 0.
        """

        params = {
            'title': self.app_name,
            'token': self.log_token if is_log else self.app_token,
            'user': self.user,
            'message': msg,
            'priority': priority,
            'monospace': monospace
        }

        try:
            requests.post(self.PUSHOVER_URL, json=params, headers=self.HEADERS)
            logger.info(f"Notification sent successfully.")
        except Exception as e:
            logger.exception("An error occurred while sending a notification to Pushover")