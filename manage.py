#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SC.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
#http://127.0.0.1:8000/login/
#http://127.0.0.1:8000/select-role/
#http://127.0.0.1:8000/recommend-doctor/
#http://127.0.0.1:8000/book_appointment/
#http://127.0.0.1:8000/faq/

# use defaultdb;
# SET SQL_SAFE_UPDATES = 0;
# UPDATE doctor_table SET specialization = LOWER(specialization);
# SET SQL_SAFE_UPDATES = 1;
