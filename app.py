from flask import Flask, request, jsonify
from database import db
from models.user import User
from models.meal import Meal
import bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "password"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3307/daily_diet'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

#View login
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if username == user.username and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)

            return jsonify({"message":"login realizado com sucesso"}), 200

    return jsonify({"message": "Credenciais invalidas"}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message":"logout realizado com sucesso"})

@app.route("/signin", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
      hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
      user = User(username=username, password=hashed_password)
      db.session.add(user)
      db.session.commit()

      return jsonify({"message" : "usuario cadastrado"}), 200

    return jsonify({"message":"Credenciais invalidas"}), 400


if __name__ == "__main__":
    app.run(debug=True)