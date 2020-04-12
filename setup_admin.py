from app import db
from app. models import User

import sys



u = User(username=sys.argv[1], email=sys.argv[2], is_admin=True)
u.set_password(sys.argv[3])

db.session.add(u)
db.session.commit()