import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import cgi
import uuid
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
from email.header         import Header

GMAIL_USERNAME = "mmszhezhi@gmail.com"
GMAIL_PASSWORD = "zhezhi9527"
smtp_server = "smtp.gmail.com"
port = 587  # For starttls


receiver_address = "274903423@qq.com"
#Setup the MIME
message = MIMEMultipart()
message['From'] = GMAIL_USERNAME
message['To'] = receiver_address
message['Subject'] = ''


from email.mime.image import MIMEImage
img = dict(title=u'Picture report…', path=r'D:\A\crypto\analysis\FIL\FIL-MA-12.jpg', cid=str(uuid.uuid4()))
msg_html = MIMEText(u'<div dir="ltr">'
                     '<img src="cid:{cid}" alt="{alt}"><br></div>'
                    .format(alt=cgi.escape(img['title'], quote=True), **img),
                    'html', 'utf-8')
msg_alternative = MIMEMultipart('alternative')
msg_alternative.attach(msg_html)


with open(img['path'], 'rb') as file:
    msg_image = MIMEImage(file.read(), name=os.path.basename(img['path']))
    message.attach(msg_image)
msg_image.add_header('Content-ID', '<{}>'.format(img['cid']))

def send():
    message.attach(MIMEText("fuck", 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(GMAIL_USERNAME, GMAIL_PASSWORD)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(GMAIL_USERNAME, receiver_address, text)
    session.quit()
send()