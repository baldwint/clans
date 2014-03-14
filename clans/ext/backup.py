"""
Backup extension for clans.

This extension adds options to automatically save local copies of your
plan before and after editing.

"""

from __future__ import print_function
import sys
import io
storage = {}


def post_load_commands(cs):
    # read configured options
    config = {}
    if cs.config.has_section('backup'):
        config.update(dict(cs.config.items('backup')))

    # then add command line arguments
    cs.commands["edit"].add_argument(
        '-b', '--backup', dest='backup_file',
        nargs='?', metavar='FILE',
        default=config.get('backup_file', False),
        help="Backup existing plan to file before editing. "
        "To print to stdout, omit filename.")
    cs.commands["edit"].add_argument(
        '-s', '--save', dest='save_edit',
        metavar='FILE',
        default=config.get('save_edit', False),
        help='Save a local copy of edited plan before submitting.')
    cs.commands["edit"].add_argument(
        '--skip-update', dest='skip_update',
        action='store_true', default=False,
        help="Don't update the plan or open it for editing.")


def post_get_edit_text(cs, plan_text):
    # store a copy of the edited plan.
    storage['orig_edit_text'] = plan_text
    backup_file = cs.args['backup_file']
    skip_update = cs.args['skip_update']

    if backup_file is False:
        pass
    elif backup_file is None:
        # print existing plan to stdout and exit
        try:
            sys.stdout.buffer.write((plan_text).encode('utf8'))
        except AttributeError:  # python 2
            sys.stdout.write(plan_text)
        skip_update = True
    elif backup_file:
        # save existing plan to file
        with io.open(backup_file, 'w', encoding='utf8', newline='') as fp:
            fp.write(plan_text)

    if skip_update:
        # this aborts the rest of the edit command
        return False


def pre_set_edit_text(cs, edited):
    # check to see if plan was edited.
    edit_was_made = edited != storage['orig_edit_text']
    save_edit = cs.args['save_edit']

    if save_edit and edit_was_made:
        # save edited file
        with io.open(save_edit, 'w', encoding='utf8', newline='') as fp:
            fp.write(edited)
