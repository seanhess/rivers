import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Email settings
smtp_server = "smtp.gmail.com"  # Example for Gmail
smtp_port = 587
email_address = "seanhess@gmail.com"
email_password = os.environ["EMAIL_PASSWORD"]


def notify_user_via_email(user_email, month, url):
    """Notify the user about the change via email."""
    # Set up the email server and login
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(email_address, email_password)
    
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = user_email
    msg['Subject'] = "River Bot Detected Changes!"
    
    body = "Meep Moop. Detected Changes in {}. \n\n{}".format(month, url)
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email and close the server connection
    server.send_message(msg)
    server.quit()

    print("Notification email has been sent.")


if __name__ == "__main__":
    notify_user_via_email("shess@nso.edu", "jun", "2024-06-01")
