# E-commerce

An e-commerce web app where user can post auction listings, place bids on listings, comment on those listings and add listings to a watchlist.

## How to install locally
```
pip install -r requirements.txt

export SECRET_KEY=<your_secret_key>

python manage.py makemigrations

python manage.py migrate

python manage.py runsever
```