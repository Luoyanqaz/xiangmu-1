"""
Celery配置文件
"""
import os
from celery import Celery

# 设置Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('xiangmu2')

# 从Django settings中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已注册app下的tasks.py文件
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
