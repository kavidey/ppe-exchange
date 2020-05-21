from app import db
from app. models import User, Hospital

import sys


h = Hospital(name="admin")
db.session.add(h)
u = User(username=sys.argv[1], email=sys.argv[2], is_admin=True, is_verified=True, hospital_id=h.id)
u.set_password(sys.argv[3])

db.session.add(u)
db.session.commit()