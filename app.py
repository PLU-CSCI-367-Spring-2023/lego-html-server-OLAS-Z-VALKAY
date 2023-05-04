from flask import Flask, request
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    "host=db dbname=postgres user=postgres password=postgres",
    cursor_factory=RealDictCursor)
app = Flask(__name__)


@app.route("/")
def hello_world():
    name = request.args.get("name", "World")
    return f"<p>Hello, {name}!</p>"
