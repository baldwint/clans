"""
Backup extension for clans.

This extension adds options to automatically save local copies of your
plan before and after editing.

"""

import sys
import os.path
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

def post_get_edit_text(cs, plan_text):
    # store a copy of the edited plan.
    storage['orig_edit_text'] = plan_text

    if cs.args.backup_file is False:
        pass
    elif cs.args.backup_file is None:
        # print existing plan to stdout and exit
        print >> sys.stdout, plan_text.encode(sys.stdout.encoding or 'utf8')
        sys.exit()
    elif cs.args.backup_file:
        # save existing plan to file
        # NB, there will be no newline at the end of the file
        fp = open(cs.args.backup_file, 'w')
        fp.write(plan_text.encode('utf8'))
        fp.close()

def pre_set_edit_text(cs, edited):
    # check to see if plan was edited.
    edit_was_made = edited != storage['orig_edit_text']

    if cs.args.save_edit and edit_was_made:
        # save edited file
        fp = open(cs.args.save_edit, 'w')
        fp.write(edited.encode('utf8'))
        fp.close()
