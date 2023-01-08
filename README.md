# Data API

## Starting the application

### 1. Using Docker

The easiest way of running the application is to go into the API directory

```cd API```

and run

```docker compose up```

### 2. Using ```manage-fastapi```

Make sure to install all the required dependencies. You can do it by going into the API directory

```cd API```

and running the following command if you're using ```pip```:

```pip3 install -r requirements.txt```

The app can then be started using

```python3 -m uvicorn app.main.app:app --reload```


## Calling the API

The above-mentioned instructions with run the app on the port 8000 of the locale machine.

You can reach the Swagger documentation by accessing ```http://localhost:8000/docs```.
