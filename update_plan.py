#!/opt/local/bin/python

import urllib2
from urllib import urlencode
import cookielib

# params
loginurl = "http://www.grinnellplans.com/index.php"
editurl = "http://www.grinnellplans.com/edit.php"
bakfile = 'plan.orig.txt'
writefile = 'update.txt'

login_info = {
    'username': 'baldwint',
    'password': 'not_my_password',
#    'username': '2008alums',
#    'password': 'alum_password',
    'submit': 'Login'
}

# make cookie jar
cj = cookielib.LWPCookieJar()

# install it into urllib2
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

# log into plans
req = urllib2.Request(loginurl)
handle = urllib2.urlopen(req, urlencode(login_info))

# grab edit page
req = urllib2.Request(editurl)
handle = urllib2.urlopen(req)

#parse out existing plan
from BeautifulSoup import BeautifulSoup
soup = BeautifulSoup(handle.read())
plan = soup.find('textarea')

# parse out plan md5
md5tag = soup.find('input', {'name': 'edit_text_md5'})
md5 = md5tag.attrMap['value']

# save existing plan
fp = open(bakfile, 'w')
fp.write(plan.text.encode('utf8'))
fp.close

# load up new plan
fp = open(writefile, 'r')
edit_info = {
    'plan': fp.read(),
    'edit_text_md5': md5,
    'submit': 'Change Plan'
}
fp.close()

# update plan
req = urllib2.Request(editurl)
handle = urllib2.urlopen(req, urlencode(edit_info))

print handle.read()

#save cookie
#cj_filename = "plans.python.cookie"
#cj.save(cj_filename)


