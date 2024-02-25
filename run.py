#!/usr/bin/python3


from app import create_app
import os

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)

if __name__ == '__main__':
        app.run(host='0.0.0.0',port=5000, debug=True)
