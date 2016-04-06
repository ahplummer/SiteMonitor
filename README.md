## SiteMonitor
###Description
This utility pings a website and retrieves the front page.  It then marks it good or bad in a local SQLite Database.  It's a cheap way of doing some 'uptime' monitoring of a website.

This will log entries into a local SQLite db called 'sitemetrics.db' for further review.
###Usage

```$python SiteMonitor.py -site=http://example.com -text=EXAMPLE -smtpserver=smtp.gmail.com:587 -smtpuser=gmailuser -smtppassword=gmailpass -fromemail=gmailuser@gmail.com -recipients=gmailuser@gmail.com -sendwhengood=FALSE```
NOTE: This is not threaded, so is best placed in a cron job for periodic purposes.

* -site (required): this is the url to test
* -text (required): Text in the HTML document retrieved to test for
* -smtpserver (optional): if you'd like an email
* -smtpuser (option): see above
* -smtppassword (optional): see above
* -recipients (optional): see above, (comma delimited list)
* -sendwhengood (optional): see above, defaults to false, helps for debugging
