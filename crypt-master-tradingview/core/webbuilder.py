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


s="""<head><meta name='viewport' content='target-densityDpi=device-dpi'/>

<style type="text/css">
html {
    margin:0;padding:0;
}
body {
    margin:0;
    padding:0;
    box-sizing:border-box;
}
</style>
</head>"""


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


def build(imgs,browser=None):
    if browser:
        height=100
    else:
        height = 35
    htmlbody = ""
    for v in imgs:
        htmlbody += f"""<img src={v['url']} alt="Smiley face" width="42" height="42" style="width:100%;height:{height}%">"""
        htmlbody += f"""<p>{v['name']}</p>"""
    return s + htmlhead + htmlbody + htmltail


