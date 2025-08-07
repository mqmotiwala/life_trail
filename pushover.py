import requests

class Pushover:
    
    HEADERS = {'Content-Type': 'application/json'}
    PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'

    def __init__(self, user_token, app_token, log_token):
        self.user_token = user_token
        self.app_token = app_token
        self.log_token = log_token

    def send_notification(self, msg, title=None, priority=0, is_log=False, monospace=0):
        """
        Make an API call to Pushover.

        Args:
            msg (str): The message text to be sent via Pushover.
            title (str): Optionally set the title for the message. If excluded, Pushover API will default to the app's name.
            priority (int): Notification priority, as defined by the Pushover API specification.
            is_log (bool): If True, the notification is sent to the Logs project using PUSHOVER_LOG_TOKEN.
                Otherwise, it is logged to the app project using PUSHOVER_APP_TOKEN.
            monospace (enum [0, 1]): Enum options based on Pushover API docs. 
                If 1, the text is monospaced. Defaults to 0.
        """

        params = {
            'title': title,
            'token': self.log_token if is_log else self.app_token,
            'user': self.user_token,
            'message': msg,
            'priority': priority,
            'monospace': monospace
        }

        requests.post(self.PUSHOVER_URL, json=params, headers=self.HEADERS)
