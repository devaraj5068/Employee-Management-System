#!/usr/bin/env python
"""
ResolveNow - Root Launcher
Allows running `python manage.py runserver` directly from the workspace root
as well as from inside the `digital_complaint_management` folder.
"""
import os
import sys
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent
    sub_dir = root_dir / 'digital_complaint_management'

    if sub_dir.exists():
        sys.path.insert(0, str(sub_dir))
        os.chdir(str(sub_dir))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        from django.core.management import execute_from_command_line
        from django.core.management.commands.runserver import Command as RunserverCommand
        RunserverCommand.default_port = '8800'
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
