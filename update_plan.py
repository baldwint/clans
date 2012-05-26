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

# -------------------------------------------
#              PLANS SCRAPEY-I
# get it? like "api" except... oh, never mind
# -------------------------------------------

def plans_login(username, password):
    """ log into plans """
    login_info = {'username': username,
                  'password': password,
                    'submit': 'Login' }
    req = urllib2.Request(loginurl)
    handle = urllib2.urlopen(req, urlencode(login_info))

#plans_login('baldwint', 'not_my_password')
plans_login('2008alums', 'alum_password')

def get_edit_text():
    """ retrieve contents of the edit plan field, plus md5 """
    # grab edit page
    req = urllib2.Request(editurl)
    handle = urllib2.urlopen(req)
    # parse out existing plan
    soup = BeautifulSoup(handle.read())
    plan = soup.find('textarea')
    if plan is None:
        raise PlansError("Couldn't get edit text, are we logged in?")
    if plus_hash:
        # parse out plan md5
        md5tag = soup.find('input', {'name': 'edit_text_md5'})
        md5 = md5tag.attrMap['value']
        return plan.text, md5
    else:
        return plan.text

#plans_login('baldwint', 'not_my_password')
#cj = plans_login('2008alums', 'wrong_password')
cj = plans_login('2008alums', 'alum_password')
plan_text, md5 = get_edit_text(plus_hash=True)

print md5
print hashlib.md5(plan_text.encode('utf8')).hexdigest()
#print plan_text.encode('utf8')

bakfile = 'plan.bak.txt'
editfile = 'plan.edited.txt'
writefile = 'fresh.txt'

# save existing plan
fp = open(bakfile, 'w')
fp.write(plan_text.encode('utf8'))
fp.close

# open plan for editing.
# cribbed from the mercurial source code, in ui.py.
fd, name = tempfile.mkstemp(suffix='.plan', text=True)

try:
    # populate the temp file with original text.
    f = os.fdopen(fd, 'w')
    f.write(plan_text.encode('utf8'))
    f.close()

    # open in $EDITOR
    editor = os.environ.get('EDITOR', 'pico')
    subprocess.call([editor, name])

    # retrieve edited text
    f = open(name)
    t = f.read()
    f.close()

    # ok, now save edited file
    fp = open(editfile, 'w')
    fp.write(t)
    fp.close()

finally:
    os.unlink(name)

# load up new plan
fp = open(writefile, 'r')
new_plan = fp.read()
fp.close()

def update_plan(newtext, md5):
    edit_info = {         'plan': newtext,
                 'edit_text_md5': md5,
                        'submit': 'Change Plan' }
    req = urllib2.Request(editurl)
    handle = urllib2.urlopen(req, urlencode(edit_info))
    soup = BeautifulSoup(handle.read())
    info = soup.find('div', {'class': 'infomessage'})
    print info

# do the plan update!
update_plan(edited, md5)

#save cookie
#cj_filename = "plans.python.cookie"
#cj.save(cj_filename)


