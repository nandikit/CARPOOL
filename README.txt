HASSAN CARPOOL - GLOBAL WEB APPLICATION

Included:
- Global-ready Flask application
- SQLite database for initial deployment
- Login for 7 users + Admin
- Shared calendar
- Multiple people on same date
- Authenticate & Freeze
- Admin unlock
- Automatic per-person cycle numbering
- Pending members remain in earlier cycles
- Auto-refresh every 5 seconds
- Mobile-friendly UI

Demo credentials:
BABU/babu123
VINAY/vinay123
GOWDA/gowda123
JHONY/jhony123
NANDI/nandi123
BALAJI/balaji123
VIDYA/vidya123
ADMIN/admin123

DEPLOYMENT:
1. Use Python 3.11+.
2. pip install -r requirements.txt
3. Set SECRET_KEY to a long random value.
4. Run: python app.py
5. For a cloud host, use its PORT environment variable.
6. SQLite is suitable for a small single-instance deployment. For multi-instance cloud hosting, migrate the DB layer to PostgreSQL.

IMPORTANT:
The demo passwords must be changed before real use. Do not expose the development server directly to the public internet; deploy behind the cloud platform's HTTPS/reverse proxy.
