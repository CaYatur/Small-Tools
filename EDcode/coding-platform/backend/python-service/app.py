from flask import Flask
from routes import execute, packages

app = Flask(__name__)

# Register routes
app.register_blueprint(execute.bp)
app.register_blueprint(packages.bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)