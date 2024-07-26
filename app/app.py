import os
import psycopg2
from flask import Flask, request

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


@app.get('/employees')
def get_emplyees():
    """ Get employees from the database
    
    Note that this function is both safe and idempotent.
    ---
    parameters:
      - name: name
        in: query
        schema:
          type: string
        description: Name of the employee
      - name: surname
        in: query
        schema:
          type: string
        description: Surname of the employee
    """
    conn = get_db_connection()
    cur = conn.cursor()
    name = request.args.get('name', None)
    surname = request.args.get('surname', None)
    query = 'SELECT * FROM persona'
    params = []

    if name is not None:
        query += ' WHERE nome = %s'
        params.append(name)

    if surname is not None:
        if len(params) > 0:
            query += ' AND cognome = %s'
        else:
            query += ' WHERE cognome = %s'
        params.append(surname)

    cur.execute(query, params)
    people = cur.fetchall()
    cur.close()
    conn.close()
    
    return people

@app.delete('/employee/<int:id>')
def delete_employee(id):
    """ Delete an employee from the database
    ---
    parameters:
      - name: id
        in: path
        schema:
          type: integer
        description: ID of the employee
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM persona WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return 'Employee deleted'

@app.put('/employee/<int:id>')
def put_employee(id):
    """Update or create an employee in the database
    
    Note that this function is idempotent.
    ---
    parameters:
      - name: id
        in: path
        schema:
          type: integer
        description: ID of the employee
    requestBody:
        required: true
        content:
            application/json:
            schema:
                type: object
                properties:
                name:
                    type: string
                surname:
                    type: string
                position:
                    type: string
                salary:
                    type: integer
    """
    conn = get_db_connection()
    cur = conn.cursor()
    data = request.get_json(force=True)
    print(data)
    print(id)
    name = data.get('name')
    surname = data.get('surname')
    position = data.get('position')
    salary = data.get('salary')

    if None in [name, surname, position, salary, id]:
        return 'Missing fields', 400
    
    try:
        cur.execute(
            'INSERT INTO persona (nome, cognome, posizione, stipendio, id) VALUES (%s, %s, %s, %s, %s)', 
            (name, surname, position, salary, id)
        )
    except psycopg2.errors.UniqueViolation:
        print('Employee already exists, updating')
        conn.rollback()
        cur.execute(
            'UPDATE persona SET nome = %s, cognome = %s, posizione = %s, stipendio = %s WHERE id = %s',
            (name, surname, position, salary, id)
        )
    conn.commit()
    cur.close()
    conn.close()
    return 'Employee created'