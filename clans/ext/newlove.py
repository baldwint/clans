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

date_fmt = '%Y-%m-%dT%H:%M:%SZ'
        # dodgy; writing 'Z' (UTC) doesn't make it true

def convert_dates(dic):
    """ If a dict has a key named 'timestamp', convert to datetimes """
    if 'timestamp' in dic:
        timestamp = datetime.strptime(dic.pop('timestamp'), date_fmt)
        dic['timestamp'] = timestamp
    return dic

class DatetimeEncoder(json.JSONEncoder):
    """ Handles encoding of datetimes as ISO 8601 format text in JSON """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(date_fmt)
        return json.JSONEncoder.default(self, obj)

def _load_log(fl):
    # ValueError would occur here if the JSON parse fails
    return json.load(fl, object_hook=convert_dates)

def _save_log(newlove, fl):
    json.dump(newlove, fl, cls=DatetimeEncoder, indent=2)

def _rebuild_log(log, results, timestamp=None):
    """
    Given results of a search, build an updated version of the log.

    This builds and returns a new log containing only entries present
    in ``results``. Results not previously seen are timestamped with
    the given time; others are passed through unmodified. If no
    timestamp is specified, the current time is used.

    This function also modifies the original log by deleting entries
    that it finds in the results. When it completes, the original log
    can be used as an index of results deleted since the original log
    was built.
    
    """
    newlog = {}

    if timestamp is None:
        timestamp = datetime.utcnow()

    # rebuild log
    for un, num, snips in results:
        old_snips = log.get(un, {})
        new_snips = {}
        for snip in snips:
            new_snips[snip] = old_snips.pop(snip,
                    dict(timestamp=timestamp, unread=True))
        newlog[un] = new_snips

    return newlog

def _flatten_log(log):
    """
    Convert the nested-dict log format to a list of lovestate dicts.

    The log is typically dictionaries of read/unread information,
    in a doubly-nested dictionary indexed by the plan name and the
    snippet. This converts that structure into a list of those dicts,
    where the former indices (plan name and snippet) are added as
    two extra entries to that dictionary.

    """
    flattened = []
    for un, snips in log.iteritems():
        for snip, lovestate in snips.iteritems():
            # make a copy when flattening
            lovestate = dict(lover=un, text=snip, **lovestate)
            flattened.append(lovestate)
    return flattened

def modify_results(results, log, order_by_time=False, only_show_new=False):
    """
    Modify the result list, in-place, to time-order or filter what is shown.

    This takes a ``results`` list reference (as is passed to the
    post_search hook) and uses the data in ``log`` to either weed out
    results marked as read (if ``only_show_new`` is True), order the
    results by the timestamp (if ``order_by_time`` is True), or both.

    If neither of these is True (default), result list is not modified.

    """
    if order_by_time:
        # flatten nested dicts
        flattened = _flatten_log(log)

        # order by time
        flattened.sort(key = lambda lovestate: lovestate['timestamp'])

        # replace search results by time-ordered quicklove
        del results[:]
        for lovestate in flattened:
            if only_show_new and not lovestate['unread']:
                continue
            note = lovestate['timestamp'].strftime(date_fmt)
            results.append((lovestate['lover'], note, [lovestate['text'],]))

    elif only_show_new:
        # don't change order, just hide snips we've seen before
        for un, count, snips in results:
            unread = [snip for snip in snips if log[un][snip]['unread']]
            snips[:] = unread

lovelog = None

def pre_search(cs, term, planlove=False):

    global lovelog

    # read configured options
    config = {}
    if cs.config.has_section('newlove'):
        config.update(dict(cs.config.items('newlove')))

    if planlove and (term == cs.username):
        # set location of log file (in app dir)
        lovelog = '{term}.love'.format(term=term)
        lovelog = os.path.join(cs.profile_dir, lovelog)


def post_search(cs, results):

    global lovelog
    if lovelog is None:
        return

    # load stored planlove
    try:
        fl = open(lovelog, 'r')
    except IOError:
        # no log file
        oldlove = {}
    else:
        oldlove = _load_log(fl)

    newlove = _rebuild_log(oldlove, results)

    # if newlove flags are thrown, modify the displayed results
    modify_results(results, newlove,
                   order_by_time=cs.args.time,
                   only_show_new=cs.args.new)

    # mark all planlove as read
    if not cs.args.keepunread:
        for dic in newlove.values():
            for lovestate in dic.values():
                if lovestate['unread']:
                    lovestate['unread'] = False

    # store log
    with open(lovelog, 'w') as fl:
        _save_log(newlove, fl)
        lovelog = None

    # TODO: option to hoard deleted love

