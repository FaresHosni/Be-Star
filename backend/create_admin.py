import requests
import sys

try:
    r = requests.post('http://localhost:8000/api/auth/init', json={
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@bestar.com'
    })
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', str(e))
