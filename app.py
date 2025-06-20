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

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
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


@app.route("/meal", methods=["POST"])
@login_required
def create_meal():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    date = data.get("date")
    isDiet = data.get("isDiet")

    if name and description and date:
        meal = Meal(name=name, description=description, date=date, isDiet=isDiet, user_id=current_user.id)
        db.session.add(meal)
        db.session.commit()

        return jsonify({"message": "Refeição criada com sucesso"}), 200
    
    return jsonify({"message": "Credenciais invalidas"}), 400

@app.route("/meal/<int:meal_id>", methods=["GET"])
def read_meal(meal_id):
    meal = Meal.query.filter_by(id = meal_id).first()

    if meal:
        return {
            "name": meal.name,
            "description": meal.description,
            "date": meal.date,
            "isDiet": meal.isDiet
        }

    return jsonify({"message":"Refeição não encontrada"}), 400

@app.route("/meal")
@login_required
def read_meals():
    meals = Meal.query.filter_by(user_id=current_user.id).all()
    meal = []
    for m in meals:
        meal.append({
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "date": m.date,
            "isDiet": m.isDiet
        })
    if meals:
        return jsonify(meal), 200
    
    return ({"message": f"Refeições não encontradas com o usuario {current_user.username}"}), 400

@app.route("/meal/<int:meal_id>", methods=["PUT"])
def update_meal(meal_id):
    data = request.json
    name = data.get("name")
    description = data.get("description")
    date = data.get("date")
    isDiet = data.get("isDiet")

    meal = Meal.query.filter_by(id = meal_id).first()

    if name and description and date and meal:
        meal.name = name
        meal.description = description
        meal.date = date
        meal.isDiet = isDiet

        db.session.commit()

        return jsonify({"message":"Refeição atualizada"}), 200

    return jsonify({"message":"Refeição invalida"}), 400


@app.route("/meal/<int:meal_id>", methods=["DELETE"])
def delete_meal(meal_id):
    meal = Meal.query.filter_by(id = meal_id).first()

    if meal:
        db.session.delete(meal)
        db.session.commit()

        return jsonify({"message":"Refeição deletada"}), 200
    
    return jsonify({"message":"Refeição invalida"}), 400


if __name__ == "__main__":
    app.run(debug=True)