#!/usr/bin/env python

# run this script to create an actions.rst file for input to Sphinx.
#
# requires: python-sphinx
#
# from the command line run `sphinx-build` against the docs directory:
# $ sphinx-build -b html docs sst_docs


import inspect
import os
import sys
import textwrap


this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(this_dir, '../src'))

from sst import actions


with open(os.path.join(this_dir, 'actions.rst'), 'w') as h:
    def _write(text):
        if text.strip() and text.startswith('\n'):
            text = text[1:]
        text = textwrap.dedent(text or '')
        h.write(text)

    head1 = """
=========================
 SST - Actions Reference
=========================

"""
    h.write(head1)
    _write(actions.__doc__)
    head2 = """
----------------
    Actions:
----------------

"""
    h.write(head2)
    _write('\n')

    for entry in sorted(actions.__all__):
        member = getattr(actions, entry)
        doc = getattr(member, '__doc__', '')

        _write(entry)
        h.write('\n')
        _write('-' * len(entry))
        h.write('\n\n')

        try:
            spec = inspect.getargspec(member)
        except TypeError:
            pass
        else:
            _write('.. function :: ')
            spec_text = inspect.formatargspec(*spec)
            h.write(entry + spec_text + '\n')
        h.write('\n    ')
        _write(doc)
        h.write('\n\n')
