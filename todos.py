from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task
from extensions import socketio
from throttling import throttle

todos = Blueprint('todos', __name__)

@todos.route('/read', methods=['GET'])
@jwt_required()
@throttle(limit=100, per=60)
def get_tasks():
    current_user = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user).all()
    tasks_list = [{'id': task.id, 'task': task.task, 'completed': task.completed} for task in tasks]
    return jsonify({'message': 'Tasks fetched successfully', 'tasks': tasks_list})

@todos.route('/add', methods=['POST'])
@jwt_required()
@throttle(limit=100, per=60)
def create_task():
    current_user = get_jwt_identity()
    task_description = request.json.get('task')
    if task_description:
        existing_task = Task.query.filter_by(task=task_description, user_id=current_user).first()
        if existing_task:
            return jsonify({'error': 'Task already exists'}), 400
        
        new_task = Task(task=task_description, completed=False, user_id=current_user)
        db.session.add(new_task)
        db.session.commit()
        
        # Emit Socket.IO event
        socketio.emit('task_update', {'action': 'add', 'task': {'id': new_task.id, 'task': new_task.task, 'completed': new_task.completed}}, room=current_user)
        
        return jsonify({'message': 'Task created', 'task': {'id': new_task.id, 'task': new_task.task, 'completed': new_task.completed}}), 201
    return jsonify({'error': 'Invalid task'}), 400

@todos.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
@throttle(limit=50, per=60)
def update_task(task_id):
    current_user = get_jwt_identity()
    try:
        updated_task_data = request.json
        task = Task.query.filter_by(id=task_id, user_id=current_user).first()
        if task:
            if 'task' in updated_task_data:
                task.task = updated_task_data['task']
            if 'completed' in updated_task_data:
                task.completed = updated_task_data['completed']
            db.session.commit()
            
            # Emit Socket.IO event
            socketio.emit('task_update', {'action': 'update', 'task': {'id': task.id, 'task': task.task, 'completed': task.completed}}, room=current_user)
            return jsonify({'message': 'Task updated successfully', 'task': {'id': task.id, 'task': task.task, 'completed': task.completed}}), 200
        return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@todos.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
@throttle(limit=50, per=60)
def delete_task(task_id):
    current_user = get_jwt_identity()
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            
            # Emit Socket.IO event
            socketio.emit('task_update', {'action': 'delete', 'task_id': task_id}, room=current_user)
            return jsonify({'message': 'Task deleted'}), 200
        return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
