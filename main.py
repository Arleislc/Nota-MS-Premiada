from werkzeug.wrappers import Request, Response
from flask import Flask, request
from nota_ms_premiada import checkCPF

app = Flask(__name__)

@app.route("/check", methods = ['GET'])
def check():
    cpf = request.args.get('cpf')
    return checkCPF(cpf)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 9000, app)