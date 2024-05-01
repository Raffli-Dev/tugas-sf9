from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    jsonify
)
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

cxn_str = 'mongodb://latihan:caplin11@ac-s43qydu-shard-00-00.xrmw0we.mongodb.net:27017,ac-s43qydu-shard-00-01.xrmw0we.mongodb.net:27017,ac-s43qydu-shard-00-02.xrmw0we.mongodb.net:27017/?ssl=true&replicaSet=atlas-b6z32o-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Latihan'
client = MongoClient(cxn_str)

db = client.dbsparta_plus_week2

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    
    msg = request.args.get('msg')
    msg1 = request.args.get('msg1', [])
    return render_template(
        'index.html',
        words=words,
        msg1=msg1,
        msg=msg
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = "0fede1f3-3b74-4e42-a6ec-eafe4a2eb077"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'main',
            msg=f'Could not find {keyword}'
        ))

    if type(definitions[0]) is str:
        array = ', '.join(definitions)
        msg1 = f'{array}'
        return redirect(url_for(
            'main',
            msg=f'Pencarianmu tidak ada {keyword} kata yang ada adalah di bawah ini : ',
            msg1=msg1
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d'),
    }

    db.words.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    db.contoh.delete_many({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was deleted',
    })

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word_give')
    example_data = db.contoh.find({'word': word})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id'))
        })
    return jsonify({
        'result': 'success',
        'example': examples
    })

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    examples = request.form.get('example')
    doc = {
        'word': word,
        'example': examples
    }

    db.contoh.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'Selamat data {examples}, anda tersimpan dan word : {word}'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.contoh.delete_one({'_id': ObjectId(id)})

    return jsonify({
        'result': 'success',
        'msg': f'Kata {word}, telah di hapus'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)