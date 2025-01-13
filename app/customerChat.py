from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from .roleDecorator import role_required
from . import db, socketio
from .models import User, Role
from datetime import datetime

customerChat = Blueprint('customerChat', __name__)

# Store active chat rooms
active_chats = {}  
# Format: {room_id: {'customer': customer_id, 'admin': admin_id, 'status': 'waiting/active'}}

@customerChat.route('/customer-chat')
@login_required
@role_required(2, 3)  # Admin roles
def customer_chat():
  # Get all active chat requests for admin view
  all_chats = {room_id: data for room_id, data in active_chats.items() if data['status'] in ['waiting', 'active']}  # Include both waiting and active chats
  active_chat_users = []
    
  for room_id, chat_data in all_chats.items():
    customer = User.query.get(chat_data['customer'])
    if customer:
      active_chat_users.append({
        'room_id': room_id,
        'customer_name': f"{customer.first_name} {customer.last_name}",
        'start_time': chat_data.get('start_time', datetime.now().strftime('%H:%M')),
        'status': chat_data['status']
      })
    
  return render_template("dashboard/customerChat/customerChat.html", user=current_user, active_chats=active_chat_users)

@customerChat.route('/api/check-auth')
def check_auth():
  return jsonify({'authenticated': current_user.is_authenticated})

@customerChat.route('/api/check-active-chat')
@login_required
def check_active_chat():
  # Check if user has an active chat
  for room_id, data in active_chats.items():
    if data['customer'] == current_user.id:
      return jsonify({
        'hasActiveChat': True,
        'roomId': room_id,
        'messages': data['messages']
      })
  return jsonify({'hasActiveChat': False})

# Socket.IO event handlers

# Customer initiates support request
@socketio.on('request_support')
def handle_support_request(data):
  if not current_user.is_authenticated:
    return
    
  # Check if user already has an active chat
  for room_id, data in active_chats.items():
    if data['customer'] == current_user.id:
      join_room(room_id)
      return
    
  room_id = f"chat_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
  active_chats[room_id] = {
    'customer': current_user.id,
    'admin': None,
    'status': 'waiting',
    'messages': [],
    'last_activity': datetime.now()
  }
    
  join_room(room_id)
    
  emit('new_chat_request', {
    'room_id': room_id,
    'customer_name': f"{current_user.first_name} {current_user.last_name}",
    'start_time': datetime.now().strftime('%H:%M')
  }, broadcast=True)
    
  emit('support_request_acknowledged', {
    'room_id': room_id,
    'message': 'Please wait for a support representative to join.'
  })

# Admin joins a specific chat room
@socketio.on('admin_join_chat')
def handle_admin_join(data):
  if not current_user.is_authenticated or current_user.role_id not in [2, 3]:
    return
    
  room_id = data['room_id']
  if room_id in active_chats:
    active_chats[room_id]['admin'] = current_user.id
    active_chats[room_id]['status'] = 'active'
        
    join_room(room_id)
        
    # Send message history to admin
    emit('chat_history', {
      'messages': active_chats[room_id].get('messages', [])
    })
        
    # Notify the customer that admin has joined
    emit('admin_joined', {
      'message': f'Support representative {current_user.first_name} has joined the chat.',
      'admin_name': current_user.first_name
    }, room=room_id)

# Handle admin leaving chat without ending it
@socketio.on('admin_leave_chat')
def handle_admin_leave(data):
  if not current_user.is_authenticated or current_user.role_id not in [2, 3]:
    return
    
  room_id = data['room_id']
  if room_id in active_chats:
    admin_name = current_user.first_name
    # Mark chat as waiting for new admin but preserve messages
    active_chats[room_id]['admin'] = None
    active_chats[room_id]['status'] = 'waiting'
        
    # Notify customer
    emit('admin_left_chat', {
      'message': 'Support representative has left the chat. Please wait for a new representative.',
    }, room=room_id)

    # Notify customer with admin's name
    emit('admin_left_chat', {
      'message': f'Support representative {admin_name} has left the chat. Please wait for a new representative.',
    }, room=room_id)
        
    # Broadcast chat request to all admins
    customer = User.query.get(active_chats[room_id]['customer'])
    emit('new_chat_request', {
      'room_id': room_id,
      'customer_name': f"{customer.first_name} {customer.last_name}",
      'start_time': datetime.now().strftime('%H:%M'),
      'status': 'waiting'
    }, broadcast=True)
        
    leave_room(room_id)

# Handle chat messages between customer and admin
@socketio.on('chat_message')
def handle_message(data):
  if not current_user.is_authenticated:
    return
    
  room_id = data['room_id']
  message = data['message']
    
  if room_id in active_chats:
    active_chats[room_id]['last_activity'] = datetime.now()
    active_chats[room_id]['messages'].append({
      'message': message,
      'type': 'outgoing' if current_user.role_id in [2, 3] else 'incoming',
      'timestamp': datetime.now().strftime('%H:%M')
    })
        
    emit('new_message', {
      'message': message,
      'sender_type': 'admin' if current_user.role_id in [2, 3] else 'customer',
      'sender_name': current_user.first_name,
      'timestamp': datetime.now().strftime('%H:%M')
    }, room=room_id)

# Handle chat ending from either customer or admin
@socketio.on('end_chat')
def handle_chat_end(data):
  if not current_user.is_authenticated:
    return
    
  room_id = data['room_id']
  ended_by = data.get('ended_by', 'system')
    
  if room_id in active_chats:
    end_message = 'Chat ended by customer.' if ended_by == 'customer' else 'Chat ended by support representative.'
        
    # Notify both parties that chat has ended
    emit('chat_ended', {
      'message': end_message
    }, room=room_id)
        
    # Clean up
    leave_room(room_id)
    del active_chats[room_id]

# Handle user disconnection
@socketio.on('disconnect')
def handle_disconnect():
  if not current_user.is_authenticated:
    return
        
  # Find and clean up any active chats for this user
  rooms_to_remove = []
  for room_id, data in active_chats.items():
    if data['customer'] == current_user.id or data['admin'] == current_user.id:
      rooms_to_remove.append(room_id)
      # Notify other participant about disconnection
      emit('user_disconnected', {
        'message': 'The other participant has disconnected.',
        'user_type': 'admin' if current_user.role_id in [2, 3] else 'customer'
      }, room=room_id)
            
  # Clean up rooms
  for room_id in rooms_to_remove:
    del active_chats[room_id]

@socketio.on('customer_leave')
def handle_customer_leave(data):
    if not current_user.is_authenticated:
        return
        
    room_id = data['room_id']
    if room_id in active_chats:
        customer = User.query.get(active_chats[room_id]['customer'])
        customer_name = f"{customer.first_name} {customer.last_name}"
        
        # Notify admin that customer left
        emit('customer_left', {
            'message': f'{customer_name} has left the chat.',
            'room_id': room_id
        }, room=room_id)

# Handle socket error
@socketio.on_error()
def error_handler(e):
  print(f'Socket.IO error: {str(e)}')
  if current_user.is_authenticated:
    emit('error', {
      'message': 'An error occurred. Please try refreshing the page.'
    })

# Add a ping/pong mechanism to keep connection alive
@socketio.on('ping_connection')
def handle_ping():
  emit('pong_connection')