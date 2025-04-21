from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    
    # 시크릿 키 설정 (세션 사용을 위해 필요)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Jinja2 환경에 min 함수 추가
    app.jinja_env.globals['min'] = min
    
    from app.routes import main_bp, cart_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(cart_bp)
    
    return app