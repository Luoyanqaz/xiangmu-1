"""Start/stop only xiangmu2's processes; never manage shared MySQL or Redis 6379."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import psutil
import redis
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / 'mature-evaluation-system-backend'
FRONTEND = ROOT / 'mature-evaluation-system-frontend'
LOCAL = ROOT / '.local'
STATE = LOCAL / 'processes.json'
CONFIG = dotenv_values(BACKEND / '.env')
ENV = {**os.environ, **{k: v for k, v in CONFIG.items() if v is not None},
       'PYTHONIOENCODING': 'utf-8', 'PYTHONUNBUFFERED': '1'}
PORTS = {'redis': 6380, 'backend': 8001, 'frontend': 5174}
DISTRO = 'Ubuntu-24.04'


def state():
    return json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {}


def save(data):
    LOCAL.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2), encoding='utf-8')


def owned_process(record):
    if not record:
        return None
    try:
        proc = psutil.Process(record['pid'])
        return proc if abs(proc.create_time() - record['created']) < 0.01 else None
    except psutil.NoSuchProcess:
        return None


def port_open(port):
    with socket.socket() as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(('127.0.0.1', port)) == 0


def redis_client():
    return redis.Redis.from_url(CONFIG['REDIS_CACHE_URL'], socket_timeout=2)


def wsl_path(path):
    return subprocess.check_output(
        ['wsl.exe', '-d', DISTRO, '--exec', 'wslpath', '-a', '-u', str(path)],
        text=True, encoding='utf-8').strip()


def commands():
    return {
        'backend': [sys.executable, str(BACKEND / 'manage.py'), 'runserver', '127.0.0.1:8001', '--noreload'],
        'worker': [sys.executable, '-m', 'celery', '-A', 'config', 'worker', '-l', 'info', '-P', 'solo',
                   '-Q', 'xiangmu2', '--hostname=xiangmu2@%h'],
        'frontend': ['node.exe', str(FRONTEND / 'node_modules/vite/bin/vite.js'),
                     '--port', '5174', '--strictPort'],
    }


def start_one(name):
    records = state()
    if owned_process(records.get(name)):
        print(f'{name}: already running (owned by xiangmu2)')
        return False
    if name in PORTS and port_open(PORTS[name]):
        raise RuntimeError(f'Port {PORTS[name]} is occupied by an untracked process; refusing to reuse or stop it.')
    LOCAL.mkdir(exist_ok=True)
    if name == 'redis':
        redis_dir = LOCAL / 'redis'
        redis_dir.mkdir(exist_ok=True)
        linux_dir = wsl_path(redis_dir)
        conf = redis_dir / 'redis.conf'
        conf.write_text('\n'.join([
            'bind 127.0.0.1', 'protected-mode yes', 'port 6380', 'daemonize no',
            f'dir "{linux_dir}"', 'dbfilename xiangmu2.rdb', 'appendonly yes',
            'appenddirname xiangmu2-aof', f'requirepass {CONFIG["REDIS_PASSWORD"]}',
            'logfile ""', 'save 60 1', '']) , encoding='utf-8')
        cmd = ['wsl.exe', '-d', DISTRO, '--exec', 'redis-server', f'{linux_dir}/redis.conf']
    else:
        cmd = commands()[name]
    cwd = FRONTEND if name == 'frontend' else BACKEND
    error_log = LOCAL / f'{name}.err.log'
    error_offset = error_log.stat().st_size if error_log.exists() else 0
    with (LOCAL / f'{name}.out.log').open('ab') as out, error_log.open('ab') as err:
        proc = subprocess.Popen(cmd, cwd=cwd, env=ENV, stdout=out, stderr=err,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    records[name] = {'pid': proc.pid, 'created': psutil.Process(proc.pid).create_time(), 'root': str(ROOT)}
    save(records)
    try:
        for _ in range(60):
            if proc.poll() is not None:
                raise RuntimeError(f'{name} exited; inspect .local/{name}.err.log')
            if name == 'worker':
                with error_log.open('rb') as log:
                    log.seek(error_offset)
                    if b'ready.' in log.read():
                        break
            elif port_open(PORTS[name]):
                if name != 'redis' or redis_client().ping():
                    break
            time.sleep(0.5)
        else:
            raise RuntimeError(f'{name} did not become ready; inspect its .local logs')
    except Exception:
        stop_one(name)
        raise
    print(f'{name}: started, PID {proc.pid}')
    return True


def stop_one(name):
    records = state()
    record = records.get(name)
    proc = owned_process(record)
    if not proc:
        records.pop(name, None)
        save(records)
        return
    if record.get('root') != str(ROOT):
        raise RuntimeError('Process belongs to a different project path. Stop it before moving the folder.')
    if name == 'redis' and port_open(6380):
        # Authentication and the configuration path must identify this instance before shutdown.
        client = redis_client()
        expected = wsl_path(LOCAL / 'redis' / 'redis.conf')
        if client.info('server').get('config_file') != expected:
            raise RuntimeError('Redis config path does not match xiangmu2; refusing shutdown.')
        client.shutdown(save=True)
    try:
        children = proc.children(recursive=True)
        for child in reversed(children):
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        proc.terminate()
        _, alive = psutil.wait_procs(children + [proc], timeout=5)
        for remaining in alive:
            remaining.kill()
    except psutil.NoSuchProcess:
        pass
    records.pop(name, None)
    save(records)
    print(f'{name}: stopped')


def check():
    sys.path.insert(0, str(BACKEND))
    os.environ.update(ENV)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from django.conf import settings
    from django.db import connection
    from django.core.cache import cache
    from django.core.files.storage import default_storage
    from django.core.files.storage import FileSystemStorage
    from config.celery import app

    assert settings.DATABASES['default']['NAME'] == 'xiangmu2'
    assert settings.DATABASES['default']['USER'] == 'xiangmu2_local'
    with connection.cursor() as cursor:
        cursor.execute('SELECT DATABASE(), CURRENT_USER()')
        db, user = cursor.fetchone()
        assert db == 'xiangmu2' and user.startswith('xiangmu2_local@')
        cursor.execute('SHOW GRANTS FOR CURRENT_USER')
        grants = [row[0] for row in cursor.fetchall()]
        assert all('USAGE ON *.*' in grant or '`xiangmu2`.*' in grant or '`xiangmu2_test`.*' in grant for grant in grants)
    assert settings.FRONTEND_URL == 'http://127.0.0.1:5174'
    assert isinstance(default_storage, FileSystemStorage)
    assert Path(default_storage.location).resolve() == (BACKEND / 'media').resolve()
    assert settings.SESSION_COOKIE_NAME == 'xiangmu2_sessionid'
    assert settings.CSRF_COOKIE_NAME == 'xiangmu2_csrftoken'
    assert settings.EMAIL_BACKEND.endswith('console.EmailBackend')
    assert not settings.LLM_ALLOW_NETWORK
    assert settings.CACHES['default']['KEY_PREFIX'] == 'xiangmu2'
    for url in [settings.CACHES['default']['LOCATION'], settings.CELERY_BROKER_URL, settings.CELERY_RESULT_BACKEND]:
        from urllib.parse import urlsplit
        assert urlsplit(url).port == 6380
    assert len({settings.CACHES['default']['LOCATION'], settings.CELERY_BROKER_URL, settings.CELERY_RESULT_BACKEND}) == 3
    cache.set('isolation_check', 'xiangmu2', 10)
    assert cache.get('isolation_check') == 'xiangmu2'
    cache.delete('isolation_check')
    assert app.conf.task_default_queue == 'xiangmu2'
    replies = app.control.ping(timeout=3)
    assert replies and all(list(reply)[0].startswith('xiangmu2@') for reply in replies), 'Own worker is not ready'
    from config.celery import debug_task
    result = debug_task.delay()
    result.get(timeout=20)
    result.forget()
    # Exercise the frontend proxy, real captcha/login, JWT and local file serving.
    import base64
    import requests
    import uuid
    session = requests.Session()
    session.trust_env = False
    base = settings.FRONTEND_URL
    page = session.get(base + '/login', timeout=10)
    page.raise_for_status()
    assert 'xiangmu2' in page.text
    response = session.get(base + '/api/auth/captcha/', timeout=10)
    response.raise_for_status()
    captcha = response.json()['data']
    assert base64.b64decode(captcha['captcha_image'].split(',', 1)[1]).startswith(b'\x89PNG')
    code = cache.get('captcha_' + captcha['captcha_key'])
    credentials = json.loads((LOCAL / 'credentials.json').read_text(encoding='utf-8'))
    response = session.post(base + '/api/auth/login/', json={
        'username': credentials['username'], 'password': credentials['password'],
        'captcha_key': captcha['captcha_key'], 'captcha_code': code,
    }, timeout=10)
    response.raise_for_status()
    auth = response.json()['data']
    assert auth['user']['username'] == credentials['username']
    session.headers['Authorization'] = 'Bearer ' + auth['access']
    response = session.get(base + '/api/auth/current-user/', timeout=10)
    response.raise_for_status()
    response = session.get(base + '/api/dashboard-stats/', timeout=10)
    response.raise_for_status()
    media_file = Path(settings.MEDIA_ROOT) / f'xiangmu2-check-{uuid.uuid4().hex}.txt'
    media_file.parent.mkdir(exist_ok=True)
    try:
        media_file.write_text('xiangmu2 isolated media', encoding='utf-8')
        response = session.get(base + '/media/' + media_file.name, timeout=10)
        response.raise_for_status()
        assert response.text == 'xiangmu2 isolated media'
    finally:
        media_file.unlink(missing_ok=True)
    print('PASS: independent database/user grants, Redis/cache/broker/results, worker task, storage, cookies and local integrations.')
    print('PASS: frontend, captcha, administrator login/JWT, dashboard API and media proxy.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'status', 'check', 'redis'])
    action = parser.parse_args().action
    if action in ('start', 'redis'):
        started = []
        try:
            for name in (['redis'] if action == 'redis' else ['redis', 'backend', 'worker', 'frontend']):
                if start_one(name):
                    started.append(name)
        except Exception:
            # Only rollback processes created by this invocation.
            for name in reversed(started):
                stop_one(name)
            raise
        print('xiangmu2: http://127.0.0.1:5174/login')
    elif action == 'stop':
        for name in ['frontend', 'worker', 'backend', 'redis']:
            stop_one(name)
    elif action == 'status':
        records = state()
        for name in ['redis', 'backend', 'worker', 'frontend']:
            proc = owned_process(records.get(name))
            print(f'{name}: ' + (f'running (PID {proc.pid})' if proc else 'stopped'))
    else:
        check()


if __name__ == '__main__':
    main()
