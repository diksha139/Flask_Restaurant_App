from app import application
from app.apis import *

from flask import Flask,jsonify
# application = Flask(__name__)

# application.app_context().push()


if __name__ == "__main__":
    print("hello")
    
    application.run(debug=True, port=8000)
    