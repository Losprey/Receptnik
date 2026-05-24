from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
SUBOR = "recepty.json"

def nacitaj():
    if not os.path.exists(SUBOR):
        return []
    with open(SUBOR, "r") as f:
        return json.load(f)

def uloz(recepty):
    with open(SUBOR, "w") as f:
        json.dump(recepty, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    recepty = nacitaj()
    return render_template('index.html', recepty=recepty)

@app.route('/pridat', methods=['POST'])
def pridat():
    nazov = request.form['nazov']
    ingrediencie = request.form['ingrediencie']
    postup = request.form['postup']
    
    recepty = nacitaj()
    recepty.append({"nazov": nazov, "ingrediencie": ingrediencie, "postup": postup})
    uloz(recepty)
    
    return redirect(url_for('index'))

@app.route('/hladat')
def hladat():
    ingrediencia = request.args.get('ingrediencia', '').lower()
    recepty = nacitaj()
    najdene = [r for r in recepty if ingrediencia in r['ingrediencie'].lower()]
    return render_template('index.html', recepty=najdene, hladany=ingrediencia)

@app.route('/ai_navrh', methods=['POST'])
def ai_navrh():
    ingrediencie = request.form['ingrediencie']
    import subprocess
    import json as j
    
    data = j.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f"Navrhni jednoduchý recept z týchto ingrediencií: {ingrediencie}. Odpovedaj po slovensky."}]
    })
    
    result = subprocess.run([
        "curl", "-s", "https://api.deepseek.com/chat/completions",
        "-H", f"Authorization: Bearer {os.environ['DEEPSEEK_API_KEY']}",
        "-H", "Content-Type: application/json",
        "-d", data
    ], capture_output=True, text=True)
    
    odpoved = j.loads(result.stdout)
    ai_text = odpoved["choices"][0]["message"]["content"]
    
    return jsonify({"navrh": ai_text})

if __name__ == '__main__':
    app.run(debug=True)
