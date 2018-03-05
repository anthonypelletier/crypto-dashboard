# Cryptocurrency Dashboard
A simple dashboard for tracking your cryptos !

## Installation instructions

1. Clone the repository
```
git clone https://github.com/anthonypelletier/crypto-dashboard/
```

1. Edit `settings.py` to setup PostgreSQL server
```
nano ./crypto-dashboard/src/dashboard/settings.py
```

2. Build image
```
docker build -t dashboard ./crypto-dashboard
```

3. Run container
```
docker run -d -p 80:80 dashboard
```

4. Launch terminal into container
```
docker exec -it dashboard /bin/bash
```

5. Create tables and superuser
```
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

## Like my work ? Make donations !
| Method       | Address                                                                          |
|:-------------|:---------------------------------------------------------------------------------|
| **Paypal**   | [https://www.paypal.me/anthonypelletier](https://www.paypal.me/anthonypelletier) |
| **Bitcoin**  | 3Low4pz96B5N9hu77e7wet8AU3GvbGGNxM                                               |
| **Ethereum** | 0xe8b9de5146dc2938a5e46492c0efe9f925562a45                                       |
