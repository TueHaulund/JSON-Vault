import celery

celery_params = {
    'broker': 'redis://localhost:6379/0',
    'backend': 'redis://localhost:6379/0',
    'include': ['jsonvault_tasks']
}

celery_app = celery.Celery('jsonvault', **celery_params)

if __name__ == '__main__':
    celery_app.start()