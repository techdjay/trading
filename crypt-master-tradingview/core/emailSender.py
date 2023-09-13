import os
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import cv2
from core.utils import imgconcat

to_addr = "274903423@qq.com"
to_addr = "2485469677@qq.com"
from_addr = "mmszhezhi@gmail.com"
password = "zhezhi9527"
smtp = 'smtp.gmail.com'
imgpath = r'D:\A\crypto\analysis\LINK\LINK_60-MA-10.jpg'

htmlhead = (
        '<html><body><h1>Latest Cypt Report</h1>' + '<p>The number of links have had a variation of <b><i>{latest_variation}</i></b> compared to <b><i>last week</i></b>.<br>' +
        'and of <b><i>{all_time_variation}</i></b> compared to <b><i>2019-10-30</i></b>.</p>'
)
htmlbody = ""
htmltail = (
        '<p>These are the 10 latest link extraction. <a href="https://drive.google.com/file/d/xxxxxxxxxxxx">View the entire report</a></p>' +
        '<h2>Top Five Values</h2>' +
        '</body></html>')

html = ('<html><body><h1>Latest Cypt Report</h1>' +
        '<p>The number of links have had a variation of <b><i>{latest_variation}</i></b> compared to <b><i>last week</i></b>.<br>' +
        'and of <b><i>{all_time_variation}</i></b> compared to <b><i>2019-10-30</i></b>.</p>' +
        '<img src="cid:image1",width="100%"><br>' +
        '<h2>Latest Link Extractions</h2>' +
        '<p>These are the 10 latest link extraction. <a href="https://drive.google.com/file/d/xxxxxxxxxxxx">View the entire report</a></p>' +
        '<h2>Top Five Values</h2>' +
        '</body></html>').format(latest_variation="fff", all_time_variation="ddd")


def send(imgs):
    try:
        htmlbody = ""
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = f'Latest {list(imgs.keys())[0].split("_")[-1]} Report From MMS' if imgs.get('isup',None) is None else f"WARNING {list(imgs.keys())[0]} {'UP' if not imgs.get('isup') else 'DOWN'}"
        msgRoot['From'] = from_addr
        msgRoot['To'] = to_addr
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText('This email was sent from Python')
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        if imgs.get('isup',None) is None:
            for k, v in imgs.items():
                if k == "isup":
                    continue
                htmlbody += f'<img src="cid:{k}",width="100%"><br>' + f'<h2>{v[0][0]}</h2><br>' + f'<li>{v[0][1]}</li><br>' + f'<li>{v[0][2]}</li>'
                fp = open(v[1], 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()

                msgImage.add_header('Content-ID', f'<{k}>')
                msgRoot.attach(msgImage)
        else:
            ip = os.path.join("warn", list(imgs.keys())[0] + "_" +  datetime.now().strftime("%m%d%H%M")+'.jpg')
            imgconcat(imgs,ip)
            htmlbody += f'<img src="cid:fuck",width="100%"><br>'
            fp = open(ip, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()

            msgImage.add_header('Content-ID', f'<fuck>')
            msgRoot.attach(msgImage)

        html = htmlhead + htmlbody + htmltail
        html.format(latest_variation=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), all_time_variation="ddd")
        msgText = MIMEText(html, 'html')
        msgAlternative.attach(msgText)

        # This example assumes the image is in the current directory

        # Send Email
        s = smtplib.SMTP(smtp, 587)
        s.starttls()
        s.login(from_addr, password)
        s.sendmail(from_addr, to_addr, msgRoot.as_string())
        print(f"email send {list(imgs.keys())[0]}")
        s.quit()
    except Exception as e:
        print(repr(e))
