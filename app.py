from flask import Flask, request, render_template, redirect, url_for
from connection import app_search, client_search, es_client
import os
import uuid

from pygments.lexers import guess_lexer
from pygments import highlight
from pygments.formatters import HtmlFormatter

 

app = Flask(__name__)
engine = os.environ['ENGINE']
es_index = 'ugly-code-submissions'

def format_lex(code):
    lexer = guess_lexer(code)
    return highlight(code, lexer, HtmlFormatter())

def reformat_code_block(results):
    for x in results:
        x['code'] = format_lex(x['code'])
        yield  x


@app.route('/')
def index():
    code_samples = client_search.list_documents(engine)
    return render_template(
            "index.html",
            code_samples=reformat_code_block(code_samples['results']),
            )


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == "POST":
        body = dict(request.form)
        body['tags'] = body['tags'].split(',')
        es_request = es_client.index(index=es_index, body=body)
        body['es_id'] = es_request['_id']
        app_search.index_documents(
                engine,
                body=[body],
                ) 
        return redirect(url_for('get', _id=es_request['_id']))
        
    return render_template('submit_code.html')


@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('query')
    response = client_search.search(engine, body={'query': q})
    meta, results = response.values()

    for x, result in enumerate(results):
        results[x]['code']['raw'] = format_lex(results[x]['code']['raw']) 

    print(results)
    return render_template(
            'search.html',
            meta=meta,
            results=results,
            query=q,
            )


@app.route('/code/<_id>')
def get(_id: str):
    result = es_client.get(es_index, id=_id)
    code_block = result['_source']
    code_block['es_id'] = result['_id']
    code_block['code'] = format_lex(code_block['code']) # lexer iterates
    return render_template('document.html', code_block=code_block)


@app.route('/api/v1/code/<_id>/update')
def update(_id: str):
    metric = request.args.get('metric')
    new_value = requests.args.get('metric_value')
    app_search.put_documents(
            engine=engine,
            body=[_id],
            params={metric: metric_value},
            )


if __name__ == '__main__':
    app.run()
