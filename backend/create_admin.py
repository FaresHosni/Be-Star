import httpx
import sys
import asyncio

async def create_admin():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post('http://localhost:8000/api/auth/init', json={
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@bestar.com'
            })
            print('Status:', r.status_code)
            print('Response:', r.text)
    except Exception as e:
        print('Error:', str(e))

if __name__ == "__main__":
    asyncio.run(create_admin())
