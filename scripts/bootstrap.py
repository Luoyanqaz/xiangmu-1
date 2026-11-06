"""Provision only xiangmu2; root credentials are read transiently, never copied."""
import argparse
import json
import os
from pathlib import Path
import secrets
import sys

import MySQLdb
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / 'mature-evaluation-system-backend'
LOCAL = ROOT / '.local'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mysql-admin-env', type=Path, required=True,
                        help='An existing local .env containing a MySQL administrator account; read only.')
    args = parser.parse_args()
    own = dotenv_values(BACKEND / '.env')
    admin = dotenv_values(args.mysql_admin_env)
    assert own['DB_NAME'] == 'xiangmu2' and own['DB_USER'] == 'xiangmu2_local'
    connection = MySQLdb.connect(host=own['DB_HOST'], port=int(own['DB_PORT']),
                                user=admin['DB_USER'], passwd=admin['DB_PASSWORD'], charset='utf8mb4')
    with connection.cursor() as cur:
        cur.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'xiangmu2'")
        if cur.fetchone():
            raise RuntimeError('xiangmu2 already exists. Refusing to reinitialize existing data.')
        cur.execute("SELECT User FROM mysql.user WHERE User = 'xiangmu2_local'")
        if cur.fetchone():
            raise RuntimeError('xiangmu2_local already exists. Refusing to change its password or privileges.')
        cur.execute('CREATE DATABASE `xiangmu2` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        for host in ['localhost', '127.0.0.1']:
            cur.execute('CREATE USER %s@%s IDENTIFIED BY %s', ('xiangmu2_local', host, own['DB_PASSWORD']))
            for db in ['xiangmu2', 'xiangmu2_test']:
                cur.execute(f'GRANT ALL PRIVILEGES ON `{db}`.* TO %s@%s', ('xiangmu2_local', host))
    connection.close()
    print('Created xiangmu2 database and schema-scoped user; existing databases unchanged.')

    sys.path.insert(0, str(BACKEND))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('init_system_config')
    call_command('init_content_pages')
    call_command('init_surveys')
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin_password = secrets.token_urlsafe(18)
    User.objects.create_superuser('admin', 'admin@xiangmu2.local', admin_password)
    LOCAL.mkdir(exist_ok=True)
    (LOCAL / 'credentials.json').write_text(json.dumps({
        'url': 'http://127.0.0.1:5174/login', 'username': 'admin', 'password': admin_password,
    }, indent=2), encoding='utf-8')
    (LOCAL / 'login.txt').write_text(
        f'xiangmu2 local administrator\nURL: http://127.0.0.1:5174/login\nUsername: admin\nPassword: {admin_password}\n',
        encoding='utf-8')
    print('Created local administrator. Credentials: .local/login.txt (git-ignored).')


if __name__ == '__main__':
    main()
