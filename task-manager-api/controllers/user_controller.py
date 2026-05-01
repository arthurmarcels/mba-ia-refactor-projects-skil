"""User controller — business logic for user operations."""
import logging
import re
from datetime import datetime, timedelta

import jwt
from database import db
from models.user import User
from models.task import Task
from config import Config

logger = logging.getLogger(__name__)


class UserController:

    @staticmethod
    def get_all_users():
        users = User.query.all()
        result = []
        for u in users:
            user_data = u.to_dict()
            user_data['task_count'] = len(u.tasks)
            result.append(user_data)
        return result

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        data = user.to_dict()
        tasks = Task.query.filter_by(user_id=user_id).all()
        data['tasks'] = [t.to_dict() for t in tasks]
        return data, 200

    @staticmethod
    def create_user(data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            return {'error': 'Nome é obrigatório'}, 400
        if not email:
            return {'error': 'Email é obrigatório'}, 400
        if not password:
            return {'error': 'Senha é obrigatória'}, 400

        if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
            return {'error': 'Email inválido'}, 400

        if len(password) < 4:
            return {'error': 'Senha deve ter no mínimo 4 caracteres'}, 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return {'error': 'Email já cadastrado'}, 409

        if role not in ['user', 'admin', 'manager']:
            return {'error': 'Role inválido'}, 400

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        db.session.add(user)
        db.session.commit()
        logger.info(f'Usuário criado: {user.id} - {user.name}')
        return user.to_dict(), 201

    @staticmethod
    def update_user(user_id, data):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        if not data:
            return {'error': 'Dados inválidos'}, 400

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
                return {'error': 'Email inválido'}, 400
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return {'error': 'Email já cadastrado'}, 409
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < 4:
                return {'error': 'Senha muito curta'}, 400
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in ['user', 'admin', 'manager']:
                return {'error': 'Role inválido'}, 400
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_dict(), 200

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        tasks = Task.query.filter_by(user_id=user_id).all()
        for t in tasks:
            db.session.delete(t)

        db.session.delete(user)
        db.session.commit()
        logger.info(f'Usuário deletado: {user_id}')
        return {'message': 'Usuário deletado com sucesso'}, 200

    @staticmethod
    def get_user_tasks(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        tasks = Task.query.filter_by(user_id=user_id).all()
        return [t.to_dict() for t in tasks], 200

    @staticmethod
    def login(data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email e senha são obrigatórios'}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Credenciais inválidas'}, 401

        if not user.check_password(password):
            return {'error': 'Credenciais inválidas'}, 401

        if not user.active:
            return {'error': 'Usuário inativo'}, 403

        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        )

        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': token
        }, 200
