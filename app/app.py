"""Questo modulo contiene un'implementazione RESTful di un'applicazione Flask per l'accesso,
la modifica e la creazione del database Accademia tramite opportune API. L'applicazione è in 
grado di gestire la richiesta di ottenere, creare, modificare e cancellare un'entità 'persona'
dal database.
"""

import os
import psycopg2
from flask import Flask, request

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='postgres_container_flask',
                            port='5432',
                            database='accademia',
                            user=os.environ['PG_USERNAME'],
                            password=os.environ['PG_PASSWORD'])
    print('Connessione al database effettuata correttamente')
    return conn

@app.get('/employee/<int:id>')
def get_employee(id):
    """ Get an employee from the database (RESTful implementation).
    
    This is both safe and idempotend.
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
    cur.execute('SELECT * FROM persona WHERE id = %s', (id,))
    employee = cur.fetchone()
    cur.close()
    conn.close()

    if employee is not None:
        employee_dict = {
            'id': employee[0],
            'nome': employee[1],
            'cognome': employee[2],
            'posizione': employee[3],
            'stipendio': employee[4]
        }
        result = {
            'result': employee_dict,
            'links': {
                'delete': f'/employee/{id}',
                'put': f'/employee/{id}'
            }
        }
        return result
    else:
        return 'Strutturato non trovato', 404

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
    return 'Strutturato eliminato'

@app.put('/employee/<int:id>')
def put_employee(id):
    """ Replace or create an employee in the database
    
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
                nome:
                    type: string
                cognome:
                    type: string
                posizione:
                    type: string
                stipendio:
                    type: integer
    """
    data = request.get_json(force=True)
    name = data.get('nome')
    surname = data.get('cognome')
    position = data.get('posizione')
    salary = data.get('stipendio')
    
    if None in [name, surname, position, salary, id]:
        data = {
            "message": "Campi mancanti",
            "data": {
                "id": id,
                "nome": name,
                "cognome": surname,
                "posizione": position,
                "stipendio": salary
            }
        }
        return data, 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
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
    
    result = {
        "message": "Strutturato registrato correttamente",
        "data": {
            "id": id,
            "nome": name,
            "cognome": surname,
            "posizione": position,
            "stipendio": salary
        },
        "links": {
            "delete": f"/employee/{id}",
        }
    }
    return result

### LIVE CODING ###
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

    result = []
    for person in people:
        person_dict = {
            'id': person[0],
            'nome': person[1],
            'cognome': person[2],
            'posizione': person[3],
            'stipendio': person[4]
        }
        result.append(person_dict)
    
    links = {
        'delete': '/employee/<int:id>',
        'put': '/employee/<int:id>'
    }

    response = {
        'result': result,
        'links': links,
    }

    return response

@app.post('/employee')
def create_employee():
    """ Non-idempotent implementation of creating an employee
    """
    conn = get_db_connection()
    cur = conn.cursor()
    data = request.get_json(force=True)
    name = data.get('nome')
    surname = data.get('cognome')
    position = data.get('posizione')
    salary = data.get('stipendio')
    
    # To make sure the method is NOT idempotent, we need to generate a unique ID for the employee
    # so that if multiple requests are made with the same data, multiple entries are created.
    cur.execute('SELECT MAX(id) FROM persona')
    id = cur.fetchone()[0]
    id += 1
    
    if None in [name, surname, position, salary]:
        return 'Missing fields', 400
    
    cur.execute(
        'INSERT INTO persona (nome, cognome, posizione, stipendio, id) VALUES (%s, %s, %s, %s, %s)', 
        (name, surname, position, salary, id)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    result = {
        "message": "Employee created",
        "data": {
            "id": id,
            "nome": name,
            "cognome": surname,
            "posizione": position,
            "stipendio": salary
        },
        "links": {
            "delete": f"/employee/{id}",
        }
    }
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)