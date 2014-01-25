#!/usr/bin/env python
"""
Provides client interface to Plans.

"""

from urllib import urlencode
import urlparse
import cookielib
import urllib2
import json
import bs4
from HTMLParser import HTMLParser
import re
from .util import plans_md5, convert_endings


class PlansError(Exception):
    """Exception raised when there is an error talking to plans."""
    pass


class PlansPageParser(HTMLParser):
    """HTML parser for GrinnellPlans pages."""

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            # parse out id of body tag
            # (can use to identify page)
            self.page_id = dict(attrs).get('id', None)
            if self.page_id is None:
                # old interface <body> tag has no attrs
                raise PlansError('Postmodern interface required')
        if tag == 'a':
            # parse out username to see who we're logged in as.
            # amazingly, the only place this reliably appears
            # is in the bug report link at the bottom of every page.
            attrs = dict(attrs)
            href = urlparse.urlparse(attrs.get('href'))
            if (href.netloc == 'code.google.com'
                    and href.path == '/p/grinnellplans/issues/entry'):
                # if this is the bug submission link
                query = urlparse.parse_qsl(href.query)
                comment = dict(query)['comment']
                # find username in submission content using brackets
                start, stop = comment.index('['), comment.index(']')
                self.username = comment[start + 1:stop]

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
        self.username = None

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

    def _parse_message(self, soup):
        """
        Scrape details from an infomessage or alertmessage div.

        Returns a dictionary of the message parameters.

        """
        kind, = soup.attrs[u'class']
        title = soup.findChild().text
        body = ''.join(t.text for t in soup.findChildren()[1:])
        message = dict(kind=kind, title=title, body=body)
        for val in message.values():
            assert type(val) == unicode
        return message

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
                      'submit': 'Login'}
        response = self._get_page('index.php', post=login_info)
        # if login is successful, we'll be redirected to home
        success = response.geturl()[-9:] == '/home.php'
        if success:
            self.parser.feed(response.read())  # parse out username
            self.username = self.parser.username
        return success

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
        soup = bs4.BeautifulSoup(html, 'html5lib')
        plan = soup.find('textarea')
        if plan is None:
            raise PlansError("Couldn't get edit text, are we logged in?")
        else:
            plan = u'' + plan.contents[0]
            # prepending the empty string somehow prevents BS from
            # escaping all the HTML characters (weird)
            assert type(plan) == unicode
            # convert to CRLF line endings
            plan = convert_endings(plan, 'CRLF')
        if plus_hash:
            # parse out plan md5
            md5sum = soup.find('input',
                    attrs={'name': 'edit_text_md5'}).attrs['value']
            # also, explicitly compute the hash, for kicks
            assert md5sum == plans_md5(plan)
            # verify that username has not changed
            assert self.username == self.parser.username
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
        # convert to CRLF line endings
        newtext = convert_endings(newtext, 'CRLF')
        newtext = newtext.encode('utf8')
        edit_info = {'plan': newtext,
                     'edit_text_md5': md5,
                     'submit': 'Change Plan'}
        html = self._get_page('edit.php', post=edit_info).read()
        soup = bs4.BeautifulSoup(html, "html5lib")
        alert = soup.find('div', {'class': 'alertmessage'})
        info = soup.find('div', {'class': 'infomessage'})
        if alert is not None:
            # some kind of error
            msg = self._parse_message(alert)
            raise PlansError(msg['body'])
        elif info is None:
            raise PlansError('Plans did not verify update')
        else:
            # probably success
            msg = self._parse_message(info)
            return msg['body']

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

    def read_plan(self, plan):
        """
        Retrieve the contents of the specified plan.

        Returns two objects: the plan header (as a python dictionary)
                             the plan text (in HTML format)

        """
        get = {'searchname': plan}
        response = self._get_page('read.php', get=get)
        soup = bs4.BeautifulSoup(response.read(), 'html5lib')
        header = soup.find('div', {'id': 'header'})
        text = soup.find('div', {'class': 'plan_text'})
        if text is None or header is None:
            # probably a nonexistent user
            alert = soup.find('div', {'class': 'alertmessage'})
            msg = self._parse_message(alert)
            raise PlansError(msg['title'])
        # convert header html into a python dictionary
        header_dict = {}
        for key in ('username', 'planname'):
            content = header.find(
                'li', {'class': key}
                ).find(
                'span', {'class': 'value'}
                ).contents
            value = str(content[0]) if len(content) > 0 else None
            header_dict[key] = value
        for key in ('lastupdated', 'lastlogin'):
            content = header.find(
                'li', {'class': key}
                ).find(
                'span', {'class': 'value'}
                ).find(
                'span', {'class': 'long'}
                ).contents
            value = str(content[0]) if len(content) > 0 else None
            header_dict[key] = value
        plan = ''.join(str(el) for el in text.contents[1:])
        # we want to return the plan formatted *exactly* how it is
        # formatted when served, but our parser will correct <hr> and
        # <br> to self closing tags. This manually corrects them back.
        plan = plan.replace('<br/>', '<br>')
        plan = plan.replace('<hr/>', '<hr>')
        # put attributes in the right order because I have OCD
        plan = re.sub(r'<a class="([^\s]*)" href="([^\s]*)">',
                      r'<a href="\2" class="\1">', plan)
        # to avoid playing whack-a-mole, we should configure the
        # parser to not do this, or else treat contents of
        # <div class="plan_text"> tags as plain text
        # (not sure if this is possible)
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
        soup = bs4.BeautifulSoup(response.read(), 'html5lib')
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
                snip = ''.join(unicode(el) for el in li.find('span').contents)
                snippets.append(snip)
            resultlist.append((unicode(user), int(count), snippets))
        return resultlist
