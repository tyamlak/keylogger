import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=None,
			  server="smtp.gmail.com",port=587,creds=()):
	if not isinstance(send_to, list):
		send_to = [send_to]

	msg = MIMEMultipart()
	msg['From'] = send_from
	msg['To'] = COMMASPACE.join(send_to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach(MIMEText(text))

	for f in files or []:
		with open(f, "rb") as fil:
			part = MIMEApplication(
				fil.read(),
				Name=basename(f)
			)
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		msg.attach(part)


	smtp = smtplib.SMTP(server,port=port)
	smtp.starttls()
	smtp.login(creds[0],creds[1])
	smtp.sendmail(send_from, send_to, msg.as_string())
	smtp.close()