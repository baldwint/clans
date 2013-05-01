"""
Newlove extension for clans.

Supports filtering for new planlove and ordering planlove by time.

"""

import json
from datetime import datetime
import os.path

def post_load_commands(cs):
    cs.commands['love'].add_argument(
               '-t', '--time', dest='time',
               action='store_true', default=False,
               help="Order results by time first seen.")
    cs.commands['love'].add_argument(
               '-n', '--new', dest='new',
               action='store_true', default=False,
               help="Only show new planlove.")
    cs.commands['love'].add_argument(
               '--keep-unread', dest='keepunread',
               action='store_true', default=False,
               help="Preserve read state of any new planlove.")

date_fmt = '%Y-%m-%d %H:%M:%S UTC'
        # dodgy; writing 'UTC' doesn't make it true

class LoveState(object):
    """ Encapsulates read state of active love. """
    def __init__(self, timestamp, unread=True, deleted=False):
        self.timestamp = timestamp  # date and time snippet first observed
        self.unread = unread        # whether love has marked read by lovee

    @classmethod
    def from_json(cls, dic):
        love = dic.pop('love', False)
        if not love:
            return dic
        else:
            timestamp = datetime.strptime(dic.pop('timestamp'), date_fmt)
            return cls(timestamp, **dic)

class LoveEncoder(json.JSONEncoder):
    """ Handles encoding of the read state as JSON """
    def default(self, obj):
        if isinstance(obj, LoveState):
            return {'love': True,
                    'timestamp': obj.timestamp.strftime(date_fmt),
                    'unread': obj.unread,
                    }
        return json.JSONEncoder.default(self, obj)

def post_search(cs, results):
    # if this is a non-planlove search, skip
    if cs.args.func.__name__ == 'love':
        # quick love
        un = cs.username
    elif cs.args.func.__name__ == 'search':
        #TODO: time-ordered searches
        return
    else:
        return

    # read configured options
    config = {}
    if cs.config.has_section('newlove'):
        config.update(dict(cs.config.items('newlove')))

    # determine lovelog location. in appdir by default, but can be
    # set in config file. username expansion works there too!
    lovelog = config.get('lovelog',
            os.path.join(cs.dirs.user_data_dir, '{username}.love')
                ).format(username=un)

    # load stored planlove
    try:
        oldlove = json.load(open(lovelog, 'r'),
                object_hook=LoveState.from_json)
    except IOError:
        # no log file
        oldlove = {}
    except ValueError:
        # file exists, but is empty
        oldlove = {}

    newlove = {}
    now = datetime.utcnow()

    # rebuild log
    for un, num, snips in results:
        old_snips = oldlove.get(un, {})
        new_snips = {}
        for snip in snips:
            new_snips[snip] = old_snips.pop(snip, LoveState(now))
        newlove[un] = new_snips

    # if newlove flags are thrown, modify the displayed results
    if cs.args.time:
        # flatten nested dicts
        flattened = []
        for un, snips in newlove.iteritems():
            for snip, ls in snips.iteritems():
                ls.lover = un
                ls.text = snip
                flattened.append(ls)

        # order by time
        flattened.sort(key = lambda ls: ls.timestamp)

        # replace search results by time-ordered quicklove
        del results[:]
        for ls in flattened:
            if cs.args.new and not ls.unread:
                continue
            note = ls.timestamp.strftime(date_fmt)
            results.append((ls.lover, note, [ls.text,]))

    elif cs.args.new:
        # don't change order, just hide snips we've seen before
        for un, count, snips in results:
            unread = [snip for snip in snips if newlove[un][snip].unread]
            snips[:] = unread

    # mark all planlove as read
    if not cs.args.keepunread:
        for dic in newlove.values():
            for ls in dic.values():
                if ls.unread:
                    ls.unread = False

    # store log
    json.dump(newlove, open(lovelog, 'w'), cls=LoveEncoder)

    # TODO: option to hoard deleted love

