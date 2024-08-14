from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from models import tasks_collection

todos = Blueprint('todos', __name__)

@todos.route('/read', methods=['GET'])
@jwt_required()


def get_tasks():
    current_user = get_jwt_identity()
    tasks = list(tasks_collection.find({'user': current_user}))
    for task in tasks:
        task['_id'] = str(task['_id'])
    return jsonify({'message': 'Tasks fetched successfully', 'tasks': tasks})


@todos.route('/add', methods=['POST'])
@jwt_required()
def create_task():
    current_user = get_jwt_identity()
    task = request.json.get('task')
    if task:
        existing_task = tasks_collection.find_one({'task': task, 'user': current_user})
        if existing_task:
            return jsonify({'error': 'Task already exists'}), 400
        
        new_task = {'task': task, 'completed': False, 'user': current_user}
        result = tasks_collection.insert_one(new_task)
        
        new_task['_id'] = str(result.inserted_id)
        
        return jsonify({'message': 'Task created', 'task': new_task}), 201
    return jsonify({'error': 'Invalid task'}), 400


@todos.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user = get_jwt_identity()
    try:
        updated_task = request.json
        result = tasks_collection.update_one(
            {'_id': ObjectId(task_id), 'user': current_user}, 
            {'$set': updated_task}
        )
        if result.matched_count:
            updated_task['_id'] = task_id
            return jsonify({'message': 'Task updated successfully', 'task': updated_task}), 200
        return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@todos.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()
    try:
        result = tasks_collection.delete_one({'_id': ObjectId(task_id), 'user': current_user})
        if result.deleted_count:
            return jsonify({'message': 'Task deleted'}), 200
        return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400