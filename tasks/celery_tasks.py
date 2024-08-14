from app import celery
from models import tasks_collection
from bson import ObjectId

@celery.task
def delete_completed_tasks(user_id):
    result = tasks_collection.delete_many({'user': user_id, 'completed': True})
    return f"Deleted {result.deleted_count} completed tasks for user {user_id}"