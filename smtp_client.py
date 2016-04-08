import smtplib
import email.utils
from email.mime.text import MIMEText

# Prompt the user for connection info
# servername = 'smtp.gmail.com:587'
servername = '127.0.0.1:587'
username = 'oikos.labs@gmail.com'
password = 'vhysnegoxaygaifq'

to_email = username
# author = 'author@example.com'
author = username
# Create the message
msg = MIMEText('Test message from PyMOTW.')
msg.set_unixfrom('author')
msg['To'] = email.utils.formataddr(('Recipient', to_email))
msg['From'] = email.utils.formataddr(('Author', author))
msg['Subject'] = 'Test from PyMOTW'

server = smtplib.SMTP(servername)
try:
    server.set_debuglevel(True)
    # identify ourselves, prompting server for supported features
    server.ehlo()
    # If we can encrypt this session, do it
    # server.login(username, password)
    # print dir(server)
    if server.has_extn('STARTTLS'):
        server.starttls()
        server.ehlo() # re-identify ourselves over TLS connection

    # server.login(username, password)
    server.sendmail(author, [to_email], msg.as_string())
finally:
    server.quit()
