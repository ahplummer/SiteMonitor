# The MIT License (MIT)
# Copyright (C) 2014 Allen Plummer, https://www.linkedin.com/in/aplummer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import argparse
import time
import urllib2
import socket

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3

def sendEmail(fromemail, htmlmessage, subject, recipients,smtpserver, user,password):
    Body = htmlmessage.encode('ascii','ignore')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromemail
    msg['To'] = ", ".join(recipients)
    # Create the body of the message (a plain-text and an HTML version).
    text = Body
    html = Body
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    smtpserver = smtplib.SMTP(smtpserver)
    if user != None and user != "":
        smtpserver.starttls()
        smtpserver.login(user, password)
    # Send the message via local SMTP server.
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    smtpserver.sendmail(fromemail, recipients, msg.as_string())
    smtpserver.quit()
    print('Sent email')

if __name__ == '__main__':
    start_time = time.time()
    parser = argparse.ArgumentParser(description='Grabs front page, looks for text, notifies.')
    parser.add_argument('-site', '--site', help='Site to monitor', required=True)
    parser.add_argument('-text', '--text', help='Text to find', required=True)
    parser.add_argument('-smtpserver', '--smtpserver', help='SMTP Server', required=False)
    parser.add_argument('-smtpuser', '--smtpuser', help='SMTP User', required=False)
    parser.add_argument('-fromemail', '--fromemail', help='From Email', required=False)
    parser.add_argument('-smtppassword', '--smtppassword', help='SMTP Password', required=False)
    parser.add_argument('-recipients', '--recipients', help='Recipients to send to', required=False)
    parser.add_argument('-sendwhengood', '--sendwhengood', help='Notify when good', required=False)

    args = vars(parser.parse_args())

    sendwhengood = False
    if args['sendwhengood'] != None and args['sendwhengood'].upper() == 'TRUE':
        sendwhengood = True
    site = args['site']
    text = args['text']
    fromemail = None
    if args['fromemail'] != None:
        fromemail = args['fromemail']
    smtpserver = None
    if args['smtpserver'] != None:
        smtpserver = args['smtpserver']
    recipientlist = []
    recipients = None
    if args['recipients'] != None:
        parts = args['recipients'].split(',')
        for p in parts:
            recipientlist.append(p)


    if site.find('http://') == -1:
        site = 'http://' + site
    print 'Attempting to find: "' + text + '", at site: ' + site
    request = urllib2.Request(site, None, {'User-Agent' : 'NotifyScripter'})
    response = urllib2.urlopen(request)
    html = response.read()

    elapsed_time = time.time() - start_time
    print 'Number of seconds: ' + str(elapsed_time)
    found = html.find(text)
    subject = 'Site Uptime Results polled from ' + socket.gethostbyname(socket.gethostname())
    message = '<h2>Site notification result for <strong>' + site + '</strong>: '
    if found > -1:
        message = message + '<span style="color:green">GOOD.</span>'
        subject = subject + ': Good'
    else:
        message = message + '<span style="color:red">FAILED!!</span>'
        subject = subject + ': Failed'
    message = message + '</h2><br/>'
    message = message + '<h4>This took ' + str(elapsed_time) + ' seconds.</h4>'


    if found == -1 or sendwhengood:
        if smtpserver == None or len(recipientlist) == 0 or fromemail == None:
            print 'Can''t send email for this message: '  + message + ', due to insufficient parameters.'
        else:
            sendEmail(fromemail,message,subject, recipientlist, smtpserver, args['smtpuser'],args['smtppassword'])

    conn = sqlite3.connect('sitemetrics.db')
    with conn:
        c = conn.cursor()
        sql = 'create table if not exists stats (id integer primary key autoincrement, stat_datetime timestamp, status varchar(10), elapsedtime double)'
        c.execute(sql)
        status = 'GOOD'
        if found == -1:
            status = 'BAD'

        sql = "insert into stats (status, stat_datetime, elapsedtime) values ('" + status + "', datetime(), " + str(elapsed_time) + ")"
        c.execute(sql)
