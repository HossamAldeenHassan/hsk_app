import json
import os
from flask import Flask, render_template, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {filename}: {e}")
        return []

def validate_vocab(item):
    required = ['id', 'lesson', 'hanzi', 'pinyin', 'arabic']
    return all(k in item and item[k] is not None for k in required)

def validate_sentence(item):
    required = ['id', 'lesson', 'hanzi', 'pinyin', 'arabic']
    return all(k in item and item[k] is not None for k in required)

def validate_dialogue(item):
    required = ['lesson', 'dialogue_id', 'lines']
    if not all(k in item for k in required):
        return False
    if not isinstance(item['lines'], list) or len(item['lines']) == 0:
        return False
    return True

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/vocab')
def get_vocab():
    raw = load_json('vocab.json')
    valid = []
    for item in raw:
        if validate_vocab(item):
            valid.append(item)
        else:
            print(f"[WARN] Skipping malformed vocab item: {item.get('id', '?')}")
    return jsonify(valid)

@app.route('/api/sentences')
def get_sentences():
    raw = load_json('sentences.json')
    valid = []
    for item in raw:
        if validate_sentence(item):
            valid.append(item)
        else:
            print(f"[WARN] Skipping malformed sentence item: {item.get('id', '?')}")
    return jsonify(valid)

@app.route('/api/dialogues')
def get_dialogues():
    raw = load_json('dialogues.json')
    flattened = []
    for item in raw:
        if not validate_dialogue(item):
            print(f"[WARN] Skipping malformed dialogue: {item.get('dialogue_id', '?')}")
            continue
        for i, line in enumerate(item['lines']):
            if not all(k in line for k in ['speaker', 'hanzi', 'pinyin', 'arabic']):
                print(f"[WARN] Skipping malformed dialogue line in dialogue_id={item['dialogue_id']}")
                continue
            flattened.append({
                'id': f"d{item['dialogue_id']}_{i}",
                'lesson': item['lesson'],
                'dialogue_id': item['dialogue_id'],
                'line_index': i,
                'speaker': line['speaker'],
                'hanzi': line['hanzi'],
                'pinyin': line['pinyin'],
                'arabic': line['arabic'],
                'title': item.get('title', ''),
                'type': 'dialogue'
            })
    return jsonify(flattened)

if __name__ == '__main__':
    print("✅ HSK1 Flashcard App running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
