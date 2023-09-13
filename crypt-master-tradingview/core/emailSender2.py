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

# to_addr = "274903423@qq.com"
# to_addr = "2485469677@qq.com"
to_addr = "2543319562@qq.com"
# to_addr = "manimaker@163.com"
# from_addr = "mmszhezhi@gmail.com"
# password = "zhezhi9527"
from_addr = "aoyamahanaali@gmail.com"
password = "herman9527"
smtp = 'smtp.gmail.com'
imgpath = r'D:\A\crypto\analysis\LINK\LINK_60-MA-10.jpg'

htmlhead = (
        '<html><body><h1>Ezekiel 25:17</h1>' +
        '<p>The path of the righteous man is beset on all sides by the iniquities of the selfish and the tyranny of evil men. Blessed is he, who in the name of charity and good will, shepherds the weak through the valley of darkness, for he is truly his brother’s keeper and the finder of lost children. And I will strike down upon thee with great vengeance and furious anger those who would attempt to poison and destroy my brothers. And you will know my name is the Lord when I lay my vengeance upon thee.</p>'

)
htmlbody = ""
htmltail = (
        '<p>These are the 10 latest link extraction. <a href="https://drive.google.com/file/d/xxxxxxxxxxxx">View the entire report</a></p>' +
        '<h2>Top Five Values</h2>' +
        '</body></html>')

html = ('<html><body><h1>Ezekiel 25:17</h1>' +
        '<p>The number of links have had a variation of <b><i>{latest_variation}</i></b> compared to <b><i>last week</i></b>.<br>' +
        'and of <b><i>{all_time_variation}</i></b> compared to <b><i>2019-10-30</i></b>.</p>' +
        '<img src="cid:image1",width="100%"><br>' +
        '<h2>Latest Link Extractions</h2>' +
        '<p>These are the 10 latest link extraction. <a href="https://drive.google.com/file/d/xxxxxxxxxxxx">View the entire report</a></p>' +
        '<h2>Top Five Values</h2>' +
        '</body></html>').format(latest_variation="fff", all_time_variation="ddd")

from core.configure import config


def send(imgs):
    # d_order = list(filter(lambda x: (config["email"][0] in x["name"] and "X1" not in x["name"]) or any([j in x["name"] for j in config["email"][1:]]), imgs))
    d_order = list(filter(lambda x: any([j in x["name"] for j in config["email"]]) and all([k not in x["name"] for k in config["exclud"]]), imgs))
    # d_order = list(filter(lambda x: any([j in x["name"] for j in config["email"]]), imgs))
    if not len(d_order) > 0:
        return
    d_order = sorted(d_order, key=lambda x: (int(x["name"][-1]), x["index"]), reverse=True)
    # d_order = d_order[:15]
    try:
        htmlbody = ""
        msgRoot = MIMEMultipart('related')
        subject = 'WARNING '
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

        table = """<table border="1"><tr><td> cryp </td><td> index </td><td> tend </td><td> sum3_pch </td><td>block</td><td> diff </td><td> cross </td></tr>"""

        for v in d_order:
            print("email sending ", v["name"])
            table += f"""<tr><td>{v["name"]}</td><td>{v["index"]}</td><td>{v["tend"]}</td><td>{v["sum3_pch"]}</td><td>{v["block_return"]}</td><td>{v["diff"]}</td><td>{v.get("cross_pch")}</td></tr>"""
            xt = "↑" if v["tend"] else "↓"
            subject += f"({v['name']}:{xt})"
            htmlbody += f'<img src="cid:{v["name"]}",width="100%"><br>'  # f'<h2>{v["step"]} - {v["continous"]}</h2><br>' + f'<li>{"**".join([w["type"] + " : " + str(w["up"]) for w in v.get("warns")])}</li><br>' + f'<li>{v["time"]}</li>'
            htmlbody += f"<li>{v['name']}</li><br>"
            htmlbody += f"<li>{v['describe']}</li><br>"
            fp = open(v["img"], 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgImage.add_header('Content-ID', f'<{v["name"]}>')
            msgRoot.attach(msgImage)
        msgRoot['Subject'] = subject
        table += "</table>"
        html = htmlhead + table + f'<p>date : {datetime.now()}</p>' + htmlbody + htmltail
        html.format(latest_variation=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), all_time_variation="ddd")
        msgText = MIMEText(html, 'html')
        msgAlternative.attach(msgText)

        # This example assumes the image is in the current directory

        # Send Email
        print("fuck send login")
        s = smtplib.SMTP(smtp, 587)
        s.starttls()
        s.login(from_addr, password)
        s.sendmail(from_addr, to_addr, msgRoot.as_string())
        print(f"email send")
        s.quit()
        return "email send"
    except Exception as e:
        return Exception("*************fuck exception " + repr(e))
