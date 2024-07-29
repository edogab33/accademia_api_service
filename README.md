# Accademia API Service

## Setup
### Prerequisiti
Aver completato l'installazione e la configurazione di PostgreSQL secondo [queste istruzioni](https://bitbucket.org/mclab/postgresql/src/master/).

### Installazione
1. Aprire una shell
2. Posizionarvi nella directory (ad es., `bd2`) che contiene il progetto relativo a PGAdmin4 e PostgreSQL (vedere link in Sez. Prerequisiti).
3. Clonare questo progetto nella directory `bd2`.
4. Avviare il container lanciando:

```sh
docker-compose up -d
```

## Utilizzo
Dopo aver eseguito l'installazione e l'avvio dei container, saranno attivi sia il server in Flask all'indirizzo `0.0.0.0:8080`, sia il database Accademia all'indirizzo `0.0.0.0:5432`. 

Il server Flask è in ascolto all'indirizzo indicato, in modo che possa ricevere richieste HTTP; ad esempio possiamo chiedere il record relativo allo strutturato con `id` uguale a 20 eseguendo una richiesta di tipo GET:

```HTTP
0.0.0.0:8080/employee/20
```