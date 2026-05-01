from database import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
    VALID_PRIORITY_RANGE = (1, 5)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
            'overdue': self.is_overdue(),
        }

    def to_dict_with_relations(self):
        """Return dict including user_name and category_name from loaded relationships."""
        data = self.to_dict()
        data['user_name'] = self.user.name if self.user else None
        data['category_name'] = self.category.name if self.category else None
        return data

    def validate_status(self, new_status):
        return new_status in self.VALID_STATUSES

    def validate_priority(self, p):
        return self.VALID_PRIORITY_RANGE[0] <= p <= self.VALID_PRIORITY_RANGE[1]

    def is_overdue(self):
        return (
            self.due_date is not None
            and self.due_date < datetime.utcnow()
            and self.status not in ('done', 'cancelled')
        )
