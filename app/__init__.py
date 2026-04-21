from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.models.site import Site       # noqa: F401
    from app.models.epreuve import Epreuve # noqa: F401

    with app.app_context():
        db.create_all()
        if Site.query.count() == 0:
            from app.seeds import seed_all
            seed_all(db)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
