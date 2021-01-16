from flask import Flask, request, render_template, redirect, url_for
from connection import app_search, client_search, es_client
import os
import uuid

from pygments.lexers import guess_lexer
from pygments import highlight
from pygments.formatters import HtmlFormatter

 

app = Flask(__name__)
engine = os.environ['ENGINE']
es_index = os.environ['ES_INDEX']


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
        app_search.index_documents(
                engine,
                body=[body],
                ) 
        return redirect(url_for('index'))
        
    return render_template('submit_code.html')


@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('query')
    response = client_search.search(engine, body={'query': q})
    meta, results = response.values()

    for x, result in enumerate(results):
        results[x]['code']['raw'] = format_lex(results[x]['code']['raw']) 

    return render_template(
            'search.html',
            meta=meta,
            results=results,
            query=q,
            )

@app.route('/code/<_id>')
def get(_id: str):
    result = client_search.get_documents(engine, body=[_id])
    result = next(reformat_code_block(result))
    return render_template('document.html', code_block=result)


if __name__ == '__main__':
    app.run()
