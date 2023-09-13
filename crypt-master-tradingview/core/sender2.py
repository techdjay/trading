import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

to_addr = ["2485469677@qq.com"]
to_addr = ["2543319562@qq.com"]
from_addr = "mmszhezhi@gmail.com"
password = "zhezhi9527"

from_addr = "aoyamahanaali@gmail.com"
password = "herman9527"
smtp = 'smtp.gmail.com'
imgpath = r'D:\A\crypto\analysis\LINK\LINK_60-MA-10.jpg'




html = ('<html><body><h1>Latest Cypt Report</h1>' +
        '<p>The number of links have had a variation of <b><i>{latest_variation}</i></b> compared to <b><i>last week</i></b>.<br>' +
        'and of <b><i>{all_time_variation}</i></b> compared to <b><i>2019-10-30</i></b>.</p>' +
        '<img src="cid:image1",width="100%"><br>' +
        '<h2>Latest Link Extractions</h2>' +
        '<p>These are the 10 latest link extraction. <a href="https://drive.google.com/file/d/xxxxxxxxxxxx">View the entire report</a></p>' +
        '<h2>Top Five Values</h2>' +
        '</body></html>').format(latest_variation="fff", all_time_variation="ddd")

for i in range(len(to_addr)):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Latest Backlink Report From GSC'
    msgRoot['From'] = from_addr
    msgRoot['To'] = to_addr[i]
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This email was sent from Python')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(html, 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    # fp = open(imgpath, 'rb')
    # msgImage = MIMEImage(fp.read())
    # fp.close()

    # Define the image's ID as referenced above
    # msgImage.add_header('Content-ID', '<image1>')
    # msgRoot.attach(msgImage)

    # Send Email
    s = smtplib.SMTP(smtp, 587)
    s.starttls()
    s.login(from_addr, password)
    s.sendmail(from_addr, to_addr[i], msgRoot.as_string())
    s.quit()
