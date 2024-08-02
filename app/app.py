"""Questo modulo contiene un'implementazione RESTful di un'applicazione Flask per l'accesso,
la modifica e la creazione del database Accademia tramite opportune API. L'applicazione è in 
grado di gestire la richiesta di ottenere, creare, modificare e cancellare un'entità 'persona'
dal database.

RISORSE:
- Documentazione Psycopg2: https://www.psycopg.org/docs/index.html
- Documentazione Flask: https://flask.palletsprojects.com/en/3.0.x/
- Metodi HTTP: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
- REST (dalla fonte, cioè Roy Thomas Fielding): 
    - https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm
    - https://ics.uci.edu/~fielding/pubs/dissertation/evaluation.htm
- JSON: https://ecma-international.org/publications-and-standards/standards/ecma-404/
- RFC Standard (qui trovate *tutto*): https://www.rfc-editor.org/rfc/rfc9110
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
    """ Get an employee from the database.
    
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
    
    cur.execute(
        """INSERT INTO persona (nome, cognome, posizione, stipendio, id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET nome = %s, cognome = %s, posizione = %s, stipendio = %s""",
        (name, surname, position, salary, id, name, surname, position, salary)
    )
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)