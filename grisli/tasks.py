import os
import time

from celery import Celery

from .gennifer_api import generateInputs, run, parseOutput

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.task_routes = {"create_grisli_task": {"queue": 'grisli'}}

@celery.task(name="create_grisli_task")
def create_grisli_task(zenodo_id, L, R, alphaMin):
    tempDir, PTData, ExpressionData = generateInputs(zenodo_id)
    outDir = run(tempDir, PTData, L, R, alphaMin)
    output = parseOutput(tempDir, outDir, PTData, ExpressionData)
    return output
