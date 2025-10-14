import os
from typing import Optional
from dotenv import load_dotenv
import resend

load_dotenv()


class ResendService:
    """Service for sending emails via Resend API"""
    
    def __init__(self):
        api_key = os.getenv("RESEND_API_KEY")
        
        if not api_key:
            raise ValueError("RESEND_API_KEY not found in environment variables")
        
        resend.api_key = api_key
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str = "Internify",
        reply_to: Optional[str] = None
    ) -> Optional[dict]:
        """
        Send an email using Resend API
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body (plain text or HTML)
            from_name: Name to display as sender
            reply_to: Email to use for replies
        
        Returns:
            Response from Resend API or None if failed
        """
        
        try:
            # Add professional footer
            email_body = self._format_email_body(body)
            
            params = {
                "from": f"{from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": email_body,
            }
            
            # Add reply-to if provided
            if reply_to:
                params["reply_to"] = reply_to
            
            # Send email
            response = resend.Emails.send(params)
            
            return response
        
        except Exception as e:
            print(f"Error sending email via Resend: {e}")
            return None
    
    def _format_email_body(self, body: str) -> str:
        """Format email body with HTML and footer"""
        
        # Convert plain text to HTML if needed
        if not body.startswith("<"):
            # Convert line breaks to <br> tags
            body = body.replace("\n", "<br>")
        
        # Add professional HTML wrapper
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .email-content {{
            margin-bottom: 30px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        .footer a {{
            color: #4f46e5;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="email-content">
        {body}
    </div>
    
    <div class="footer">
        <p>This email was sent via <a href="https://internify.app" target="_blank">Internify</a></p>
        <p style="font-size: 11px; color: #999;">
            If you'd like to stop receiving emails from this sender, please reply directly to them.
        </p>
    </div>
</body>
</html>
"""
        return html_body
    
    async def send_batch_emails(
        self,
        emails: list[dict]
    ) -> list[Optional[dict]]:
        """
        Send multiple emails in batch
        
        Args:
            emails: List of email dictionaries with keys: to, subject, body
        
        Returns:
            List of responses from Resend API
        """
        results = []
        
        for email in emails:
            result = await self.send_email(
                to_email=email.get("to"),
                subject=email.get("subject"),
                body=email.get("body"),
                reply_to=email.get("reply_to")
            )
            results.append(result)
        
        return results


# Singleton instance
resend_service = ResendService()
