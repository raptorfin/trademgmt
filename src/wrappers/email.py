from email.mime.text import MIMEText
import smtplib

DATA=""
SMTP_SERVER = "mail.raptorfinllc.com"
SMTP_PORT = 25
SMTP_USERNAME = "admin@raptorfinllc.com"
SMTP_PASSWORD = "xRS1VczBJRHu9P"

EMAIL_TO = []
EMAIL_FROM = "admin@raptorfinllc.com"
EMAIL_SUBJECT = ""

#DATE_FORMAT = "%d/%m/%Y"
EMAIL_SPACE = ", "

def send_email():
	msg = MIMEText(DATA)
	msg['Subject'] = EMAIL_SUBJECT
	#msg['Subject'] = EMAIL_SUBJECT + " %s" % (date.today().strftime(DATE_FORMAT))
	msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
	msg['From'] = EMAIL_FROM
	mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	mail.starttls()
	mail.login(SMTP_USERNAME, SMTP_PASSWORD)
	mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
	mail.quit()