# Fix Flask DB Migrate Instructions

1. Fix database state issues w/ DB Migrate: `flask db stamp head`
2. Update DB with new changes from models.py: `flask db migrate`
3. Apply new changes: `flask db upgrade`
