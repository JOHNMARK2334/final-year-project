from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # Use DATABASE_URL from environment or fallback to local Postgres
    import os
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://medical_assistant1_user:CqhjQalOFodFEUKuTZrQJDUnaXgAMU8D@dpg-d2ep9pbuibrs738978eg-a.oregon-postgres.render.com/medical_assistant1'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
