#!/usr/bin/env python
from django.core.management import execute_manager


import settings  # assumed to be in the same directory.


if __name__ == "__main__":
    execute_manager(settings)
