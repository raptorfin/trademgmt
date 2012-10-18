from email.mime.text import MIMEText
import smtplib


def init_mail(server, user, pwd, port=25):
	server = smtplib.SMTP(server, port)
	server.starttls()
	server.login(user, pwd)
	return server


def send_email(mconn, mailto, mailfrom, mailsub, msgbody):
	msg = MIMEText(msgbody)
	msg['Subject'] = mailsub
	msg['To'] = mailto
	msg['From'] = mailfrom
	mconn.sendmail(mailfrom, mailto, msg.as_string())
	mconn.quit()
