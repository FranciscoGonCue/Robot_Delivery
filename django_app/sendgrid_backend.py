"""
Custom SendGrid Email Backend using REST API
This bypasses SSL certificate issues with SMTP
"""

import os
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


class SendGridAPIBackend(BaseEmailBackend):
    """
    A Django email backend that uses SendGrid's REST API instead of SMTP.
    This is more reliable and doesn't have SSL certificate issues.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY environment variable is not set")
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent.
        """
        if not self.client:
            if not self.fail_silently:
                raise ValueError("SendGrid client is not initialized")
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                self._send(message)
                num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
        
        return num_sent
    
    def _send(self, email_message):
        """Send a single email message"""
        from_email = Email(email_message.from_email)
        to_email = To(email_message.to[0])  # SendGrid API handles one recipient at a time
        subject = email_message.subject
        
        # Determine content type
        if email_message.content_subtype == 'html':
            content = Content("text/html", email_message.body)
        else:
            content = Content("text/plain", email_message.body)
        
        mail = Mail(from_email, to_email, subject, content)
        
        # Send email
        response = self.client.send(mail)
        
        # SendGrid returns 202 for success
        if response.status_code not in [200, 201, 202]:
            raise Exception(f"SendGrid API returned {response.status_code}: {response.body}")
        
        return True
