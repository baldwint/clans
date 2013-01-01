#!/usr/bin/env python
"""
Provides client interface to Plans.

"""

from urllib import urlencode
import cookielib
import urllib2
import json
import BeautifulSoup as bs3
from HTMLParser import HTMLParser
from hashlib import md5

class PlansError(Exception):
    """Exception raised when there is an error talking to plans."""
    pass

class PlansPageParser(HTMLParser):
    """HTML parser for GrinnellPlans pages."""

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            # parse out id of body tag
            # (can use to identify page)
            for key, value in attrs:
                if key == 'id': self.page_id = value
        if tag == 'input':
            # parse edit text md5 from input tag.
            # in the current plans implementation,
            # the syntax is < > and not < />
            attrs = dict(attrs)
            if attrs.get('name') == 'edit_text_md5':
                self.edit_text_md5 = attrs['value']

# -------------------------------------------
#              PLANS SCRAPEY-I
# get it? like "api" except... oh, never mind
# -------------------------------------------

class PlansConnection(object):
    """
    Encapsulates an active login to plans.

    """

    def __init__(self, cookiejar=None,
                 base_url="http://www.grinnellplans.com"):
        """
        Create a new plans connection.

        Optional keyword arguments:

        cookiejar -- an existing cookielib.CookieJar to store
                     credentials in.
        base_url --  URL at which to access plans, no trailing slash.

        """
        self.base_url = base_url
        if cookiejar is None:
            self.cookiejar = cookielib.LWPCookieJar()
        else:
            self.cookiejar = cookiejar
        proc = urllib2.HTTPCookieProcessor(self.cookiejar)
        self.opener = urllib2.build_opener(proc)
        self.parser = PlansPageParser()

    def _get_page(self, name, get=None, post=None):
        """
        Retrieve an HTML page from plans.

        """
        url = '/'.join((self.base_url, name))
        if get is not None:
            url = '?'.join((url, urlencode(get)))
        req = urllib2.Request(url)
        if post is not None:
            post = urlencode(post)
        try:
            handle = self.opener.open(req, post)
        except urllib2.URLError:
            err = "Check your internet connection. Plans could also be down."
            raise PlansError(err)
        return handle

    def plans_login(self, username='', password=''):
        """
        Log into plans.

        Returns True on success, False on failure. Leave username and
        password blank to check an existing login.

        """
        # the provided username and password ONLY get checked
        # by the plans server if our cookie is expired.
        # hence, if we've logged in recently, this will return True even
        # if un/pw are not provided or are otherwise bad.
        login_info = {'username': username,
                      'password': password,
                        'submit': 'Login' }
        response = self._get_page('index.php', post=login_info)
        # if login is successful, we'll be redirected to home
        return response.geturl()[-9:] == '/home.php'

    def get_edit_text(self, plus_hash=False):
        """
        Retrieve contents of the edit plan field.

        Optionally, simultaneously retrieve the md5 hash of
        the edit text, as computed on the server side.

        """
        # grab edit page
        html = self._get_page('edit.php').read()
        # Convert to unicode.
        # This will fail hard if plans ever serves invalid UTF-8.
        html = html.decode('utf-8')
        # parse out existing plan
        soup = bs3.BeautifulSoup(html, fromEncoding='utf-8')
        plan = soup.find('textarea')
        if plan is None:
            raise PlansError("Couldn't get edit text, are we logged in?")
        else:
            plan = plan.text
            assert type(plan) == unicode
        if plus_hash:
            # parse out plan md5
            self.parser.feed(html)
            md5sum = self.parser.edit_text_md5
            # also, explicitly compute the hash, for kicks
            assert md5sum == md5(plan.encode('utf8')).hexdigest()
            return plan, md5sum
        else:
            return plan

    def set_edit_text(self, newtext, md5):
        """
        Update plan with new content.

        To prevent errors, the server does a hash check on the existing
        plan before replacing it with the new one. We provide an
        md5 sum to confirm that yes, we really want to update the plan.

        Returns info message.

        """
        newtext = newtext.encode('utf8')
        edit_info = {         'plan': newtext,
                     'edit_text_md5': md5,
                            'submit': 'Change Plan' }
        html = self._get_page('edit.php', post=edit_info).read()
        soup = bs3.BeautifulSoup(html, fromEncoding='utf-8')
        #TODO: what if the edit fails? catch warnings as well.
        info = soup.find('div', {'class': 'infomessage'})
        return str(info)

    def get_autofinger(self):
        """
        Retrieve all levels of the autofinger (autoread) list.

        Returns a dictionary where the keys are the group names
        "Level 1", "Level 2", etc. and the values are a list of
        usernames waiting to be read.

        """
        # this actually doesn't scrape; there's a function for it
        # in the old JSON API.
        get = {'task': 'autofingerlist'}
        response = self._get_page('api/1/index.php', get=get)
        data = json.loads(response.read())
        # the returned JSON is crufty; clean it up
        autofinger = {}
        for group in data['autofingerList']:
            name = "Level %s" % group['level']
            autofinger[name] = group['usernames']
        return autofinger

    def read_plan(self, plan, formatted=True):
        """
        Retrieve the contents of the specified plan.

        Returns two objects: the plan header (as a python dictionary)
                             the plan text (in HTML format)

        """
        get = {'searchname': plan}
        response = self._get_page('read.php', get=get)
        soup = bs3.BeautifulSoup(response.read(), fromEncoding='utf-8')
        header = soup.find('div', {'id': 'header'})
        text = soup.find('div', {'class': 'plan_text'})
        if not formatted:
            # return raw beautifulsoup objects
            # (complete with wrapper <div>)
            return header, text
        # convert header html into a python dictionary
        header_dict = {}
        for key in ('username', 'planname'):
            value = header.find(
                        'li', {'class': key}
                    ).find(
                        'span', {'class': 'value'}
                    ).contents[0]
            header_dict[key] = str(value)
        for key in ('lastupdated', 'lastlogin'):
            value = header.find(
                        'li', {'class': key}
                    ).find(
                        'span', {'class': 'value'}
                    ).find(
                        'span', {'class': 'long'}
                    ).contents[0]
            header_dict[key] = str(value)
        # format plan text
        planlets = []
        for souplet in text.contents[1:]:
            if (u'class', u'sub') in souplet.attrs:
                # extract contents of <p class="sub">
                planlet = ''.join([str(el) for el in souplet.contents])
            else:
                planlet = str(souplet)
            planlets.append(planlet)
        plan = ''.join(planlets)
        return header_dict, plan

    def search_plans(self, term, planlove=False):
        """
        Search plans for the provided ``term``.

        If ``planlove`` is ``True``, ``term`` is a username, and the
        search will be for incidences of planlove for that user.

        returns: list of plans upon which the search term was found.
        each list element is a 3-tuple:
         - plan name
         - number of occurrences of search term on the plan
         - list of plan excerpts giving context

        the length of the excerpt list may be equal to or less than
        the number of occurrences of the search term, since
        overlapping excerpts are consolidated.

        """
        get = {'mysearch': term,
               'planlove': int(bool(planlove))}
        response = self._get_page('search.php', get=get)
        soup = bs3.BeautifulSoup(response.read(), fromEncoding='utf-8')
        results = soup.find('ul', {'id': 'search_results'})
        # results are grouped by the plan
        # on which the result was found
        user_groups = results.findAll(
                'div', {'class': 'result_user_group'})
        resultlist = []
        for group in user_groups:
            user = group.find('a', {'class': 'planlove'}).contents[0]
            count = group.find('span').contents[0]
            # now extract snippets
            snippetlist = group.findAll('li')
            snippets = []
            for li in snippetlist:
                snip = ''.join(str(el) for el in li.find('span').contents)
                snippets.append(snip)
            resultlist.append((str(user), int(count), snippets))
        return resultlist

