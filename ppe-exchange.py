from app import app, db
from app.models import User, Hospital, PPE, Wants, Has


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Hospital': Hospital, 'PPE': PPE}
