# -----------------------------------------------------------------------------
# File: activity_report
# Description: Generate a report of what was uploaded in a given day
# Date: 22 April 2015
# -----------------------------------------------------------------------------
from oda.apps.odaweb.models import OdaMaster
from django.core.management.base import BaseCommand
import os
from datetime import date, timedelta
from subprocess import Popen, PIPE
import hashlib
from django.contrib.auth.models import User
import MySQLdb

# import smtplib for the actual sending function
import smtplib

# import the email modules we'll need
from email.mime.text import MIMEText

from collections import namedtuple
from django.template import Template, Context
from django.conf import settings
#settings.configure() # We have to do this to use django templates standalone - see
# http://stackoverflow.com/questions/98135/how-do-i-use-django-templates-without-the-rest-of-django

# pointer to upload directory
UPLOAD_DIR = '/tmp/odaweb2/uploads'

# email addresses of sender and receivers
SENDER = 'admin@onlinedisassembler.com'
RECEIVERS = [
    'anthony@onlinedisassembler.com',
    'tom@onlinedisassembler.com',
    'davis@onlinedisassembler.com'
]

# our template (could just as easily be stored in a separate file)
template = """
<html>
<head>
<title>ODA Upload Report {{ date }}</title>
<link rel="stylesheet" type="text/css" href="http://www.onlinedisassembler.com/static2/css/oda2.css" />
</head>
<body>
<h3>{{ date }}</h3>

Total File Uploads: {{ total_uploads }}<br>
Total Bytes Uploaded: {{ total_bytes|filesizeformat }}<br>
Unique Files: {{ unique_files }}<br>
Unique IPs: {{ unique_ips }}<br>
Unique User Accounts: {{ unique_users }}<br>
<br>

<div style="border:3px solid #6B7C70; border-radius: 6px; float:left">
<table cellpadding="3" style="border:0px solid #6B7C70; border-spacing: 0;">
    <thead>
        <tr style="background-color:#6B7C70;color:white;font-weight:bold; padding: 5px">
            <!--<th align="left" style="padding: 2px 15px; -moz-border-radius: 6px 0 0 0; -webkit-border-radius: 6px 0 0 0;border-radius: 6px 0 0 0;">File Name</th>-->
            <th align="left" style="padding: 2px 15px;">File Name</th>
            <th>File Size</th>
            <th>File Description</th>
            <th>File MD5</th>
            <th>IP Address</th>
            <!--<th style="-moz-border-radius: 0 6px 0 0; -webkit-border-radius: 0 6px 0 0;border-radius: 0 6px 0 0;">Time</th>-->
            <th>Time</th>
        </tr>
    </thead>
    <tbody>
        {% for upload in uploads %}
        <tr style="background-color:{% cycle '#B2CEBB' '#FFFFFF' %}">
            <td style="padding: 2px 15px;"><a href=http://www.onlinedisassembler.com/odaweb/{{ upload.shortname }}>{{ upload.filename }}</a></td>
            <td style="padding: 2px 15px;">{{ upload.size|filesizeformat }}</td>
            <td style="padding: 2px 15px;">{{ upload.desc }}</td>
            <td style="padding: 2px 15px; font-family:monospace">{{ upload.md5 }}</td>
            <td style="padding: 2px 15px;">{{ upload.ip }}</td>
            <td style="padding: 2px 15px;">{{ upload.date }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
</div>
</body>
</html>
"""


def generate_report(day):

    unique_ips = []
    unique_md5s = []
    total_bytes = 0
    uploads = []
    Upload = namedtuple('Upload', 'date shortname filename ip desc size md5')

    # fetch all the new oda masters from today
    oda_masters = OdaMaster.objects.filter(creation_date__startswith=day)
    users_new = User.objects.filter(date_joined__startswith=day)
    users_all = User.objects.all()

    for m in oda_masters:

        filename = m.odb_file.binary.name()
        desc = m.odb_file.binary.desc()[0:48]
        size = m.odb_file.binary.size()
        total_bytes += size
        md5 = m.odb_file.binary.md5()
        if md5 not in unique_md5s:
            unique_md5s.append(md5)
        md5 = "%s...%s" % (md5[0:6], md5[-6:])

        timestamp = m.creation_date.strftime('%I:%M:%S %p')

        if m.ipAddress not in unique_ips:
            unique_ips.append(m.ipAddress)

        u = Upload(timestamp, m.short_name, filename, m.ipAddress, desc=desc, size=size, md5=md5)
        uploads.append(u)

    t = Template(template)
    c = Context({
        'uploads': uploads,
        'date': day.strftime('%A, %B %d, %Y'),
        'total_uploads': len(oda_masters),
        'total_bytes': total_bytes,
        'unique_files': len(unique_md5s),
        'unique_ips': len(unique_ips),
        'unique_users': len(users_all),
        'new_users': len(users_new),
        })

    return t.render(c)

def email(day, report):
    # Create a text/plain message
    msg = MIMEText(report.encode('utf-8'), 'html', _charset='utf-8')

    msg['Subject'] = 'ODA Upload Report %s' % day.strftime('%m/%d/%y')
    msg['From'] = SENDER
    msg['To'] =''.join(['%s, ' % i for i in RECEIVERS])

    print report
    return

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    s.login('avderos', 'waPupkQLKN3ZI')
    s.sendmail(SENDER, RECEIVERS, msg.as_string())
    s.quit()


class Command(BaseCommand):
    args = 'format=<text|email>'
    help = 'Example: ./migrate.py report_activity'

    def handle(self, *args, **options):
        yesterday=date.today() - timedelta(1)
        report = generate_report(yesterday)
        email(yesterday, report)
