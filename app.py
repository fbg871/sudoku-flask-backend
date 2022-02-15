from re import S
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import ForeignKey
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:" "@localhost/sudoku_dev"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Settings(db.Model):
    id = db.column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
    errorCheck = db.Column(db.String(20), default="solution")
    highlightRelated = db.Column(db.Boolean, default=False)
    prefillCell = db.Column(db.Boolean, default=False)
    focusMode = db.Column(db.Boolean, default=False)
    darkMode = db.Column(db.Boolean, default=True)
    border = db.Column(db.Boolean, default=False)
    autoRemove = db.Column(db.Boolean, default=True)

    def __init__(self, errorCheck, highlightRelated, prefillCell, focusMode, darkMode, border, autoRemove):
        self.errorCheck = errorCheck
        self.highlightRelated = highlightRelated
        self.prefillCell = prefillCell
        self.focusMode = focusMode
        self.darkMode = darkMode
        self.border = border
        self.autoRemove = autoRemove



class Puzzle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
    title = db.Column(db.String(50))
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    values = db.Column(db.String(400))
    solution = db.Column(db.String(400))
    prefilled = db.Column(db.String(400))
    totalLikes = db.Column(db.Integer, default=0)

    def __init__(self, title, description, values, solution, prefilled):
        self.title = title
        self.description = description
        self.values = values
        self.solution = solution
        self.prefilled = prefilled


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

class Progress(db.Model):
    puzzle_id = db.Column(db.Integer, ForeignKey("puzzle.id"))
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
    values = db.Column(db.String(300))
    pencilmarks = db.Column(db.String(400))
    errorIndex = db.Column(db.Integer, default = -1)


class PuzzleSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "user_id",
            "title",
            "description",
            "created_at",
            "values",
            "solution",
            "prefilled",
            "totalLikes",
        )


# serialize one puzzle
puzzle_schema = PuzzleSchema()
# multi
puzzles_schema = PuzzleSchema(many=True)


@app.route("/getpuzzle", methods=["GET"])
def get_puzzles():
    all_puzzles = Puzzle.query.all()
    results = puzzles_schema.dump(all_puzzles)
    return jsonify(results)


@app.route("/getpuzzle/<id>", methods=["GET"])
def puzzle_details(id):
    puzzle = Puzzle.query.get(id)
    return puzzle_schema.jsonify(puzzle)


@app.route("/addpuzzle", methods=["POST"])
def add_puzzle():
    title = request.json["title"]
    description = request.json["description"]
    values = request.json["values"]
    solution = request.json["solution"]
    prefilled = request.json["prefilled"]

    puzzle = Puzzle(title, description, values, solution, prefilled)
    db.session.add(puzzle)
    db.session.commit()
    return puzzle_schema.jsonify(puzzle)


if __name__ == "__main__":
    app.run(debug=True)
