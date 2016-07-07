import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
sender = 'wx_louis.luo@zeusis.com'
smtpserver = 'smtp.mxhichina.com'
receiver = 'wx_louis.luo@zeusis.com'

def send_email(subject):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['Cc'] = receiver
    msgRoot['To'] = receiver
    fd = open('report.html', 'r')
    report = fd.read()
    fd.close()
    msgText = MIMEText(report,'html','utf-8')
    msgRoot.attach(msgText)
    smtp = smtplib.SMTP(smtpserver)
    try:
        smtp.login(sender, "June,2016")
        smtp.sendmail(sender, receiver, msgRoot.as_string())
        smtp.quit()
    except:
        print "Send email fail!"

if __name__ == "__main__":
    send_email("test")
