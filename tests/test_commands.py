import pytest

import sys
if sys.version_info >= (3, 3):
    import unittest.mock as mock
else:
    import mock

from clans import ui


@pytest.fixture
def cs():
    from clans.ui import ClansSession
    cs = mock.Mock(spec=ClansSession)
    cs.args = mock.Mock()
    return cs


@pytest.fixture
def pc():
    from clans.scraper import PlansConnection
    pc = mock.Mock(spec=PlansConnection)
    return pc


@pytest.fixture
def fmt():
    from clans.fmt import RawFormatter
    fmt = mock.Mock(spec=RawFormatter)
    return fmt


def test_autoread(cs, pc, fmt):
    d = dict()
    pc.get_autofinger.return_value = d

    ui.autoread(cs, pc, fmt)
    assert pc.get_autofinger.called
    fmt.print_autoread.assert_called_with(d)


@pytest.mark.parametrize('term,love', [
    ('foo', False),
    ('bar', True),
    ])
def test_search(cs, pc, fmt, term, love):
    l = list()
    cs.args.term = term
    cs.args.love = love
    pc.search_plans.return_value = l

    ui.search(cs, pc, fmt)
    cs.hook.assert_any_call('pre_search', term, planlove=love)
    pc.search_plans.assert_called_with(term, planlove=love)
    cs.hook.assert_called_with('post_search', l)
    fmt.print_search_results.assert_called_with(l)


def test_love(cs, pc, fmt):
    l = list()
    pc.username = 'foo'
    pc.search_plans.return_value = l

    ui.love(cs, pc, fmt)
    cs.hook.assert_any_call('pre_search', 'foo', planlove=True)
    pc.search_plans.assert_called_with('foo', planlove=True)
    cs.hook.assert_called_with('post_search', l)
    fmt.print_search_results.assert_called_with(l)


def test_watch(cs, pc, fmt):
    l = list()
    pc.planwatch.return_value = l

    ui.watch(cs, pc, fmt)
    #pc.planwatch.assert_called_with(hours=12)
    fmt.print_list.assert_called_with(l)
