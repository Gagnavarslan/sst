#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Add the parent directory to the python path
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, parent_dir)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
