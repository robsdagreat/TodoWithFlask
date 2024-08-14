from app import socketio
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity

@socketio.on('join')
@jwt_required()
def on_join(data):
    username = get_jwt_identity()
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{username} has entered the room.'}, room=room)

@socketio.on('leave')
@jwt_required()
def on_leave(data):
    username = get_jwt_identity()
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{username} has left the room.'}, room=room)

@socketio.on('new_task')
@jwt_required()
def handle_new_task(data):
    emit('task_update', data, broadcast=True)