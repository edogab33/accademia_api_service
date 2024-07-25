import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

def get_db_connection():
    print(os.environ['PG_USERNAME'])
    print(os.environ['PG_PASSWORD'])
    conn = psycopg2.connect(host='127.0.0.1',
                            port='5432',
                            database='accademia',
                            user=os.environ['PG_USERNAME'],
                            password=os.environ['PG_PASSWORD'])
    print('Database connection established')
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM persona;')
    people = cur.fetchall()
    cur.close()
    conn.close()