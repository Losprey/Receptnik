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
    kategoria = request.args.get('kategoria', 'vsetky')
    if kategoria != 'vsetky':
        recepty = [r for r in recepty if r.get('kategoria') == kategoria]
    return render_template('index.html', recepty=recepty, aktivna_kategoria=kategoria)

@app.route('/api/recepty')
def api_recepty():
    recepty = nacitaj()
    return jsonify(recepty)

@app.route('/api/recepty/<int:index>')
def api_recept_detail(index):
    recepty = nacitaj()
    if 0 <= index < len(recepty):
        return jsonify(recepty[index])
    return jsonify({"error": "Recept neexistuje"}), 404

@app.route('/api/recepty', methods=['POST'])
def api_pridat_recept():
    data = request.get_json()
    if not data or 'nazov' not in data or 'ingrediencie' not in data or 'postup' not in data:
        return jsonify({"error": "Chybajú povinné polia (nazov, ingrediencie, postup)"}), 400
    
    recepty = nacitaj()
    novy_recept = {
        "nazov": data['nazov'],
        "ingrediencie": data['ingrediencie'],
        "postup": data['postup'],
        "kategoria": data.get('kategoria', ''),
        "favorite": data.get('favorite', False)
    }
    recepty.append(novy_recept)
    uloz(recepty)
    return jsonify(novy_recept), 201

@app.route('/api/recepty/<int:index>', methods=['PUT'])
def api_upravit_recept(index):
    recepty = nacitaj()
    if 0 <= index < len(recepty):
        data = request.get_json()
        if 'nazov' in data:
            recepty[index]['nazov'] = data['nazov']
        if 'ingrediencie' in data:
            recepty[index]['ingrediencie'] = data['ingrediencie']
        if 'postup' in data:
            recepty[index]['postup'] = data['postup']
        if 'kategoria' in data:
            recepty[index]['kategoria'] = data['kategoria']
        if 'favorite' in data:
            recepty[index]['favorite'] = data['favorite']
        uloz(recepty)
        return jsonify(recepty[index])
    return jsonify({"error": "Recept neexistuje"}), 404

@app.route('/api/recepty/<int:index>', methods=['DELETE'])
def api_zmazat_recept(index):
    recepty = nacitaj()
    if 0 <= index < len(recepty):
        zmazany = recepty.pop(index)
        uloz(recepty)
        return jsonify(zmazany)
    return jsonify({"error": "Recept neexistuje"}), 404

@app.route('/api/kategorie')
def api_kategorie():
    recepty = nacitaj()
    kategorie = set()
    for r in recepty:
        if r.get('kategoria'):
            kategorie.add(r['kategoria'])
    return jsonify(sorted(list(kategorie)))

@app.route('/api/statistiky')
def api_statistiky():
    recepty = nacitaj()
    pocet = len(recepty)
    oblubene = len([r for r in recepty if r.get('favorite')])
    kategorie = {}
    for r in recepty:
        kat = r.get('kategoria', 'bez kategorie')
        kategorie[kat] = kategorie.get(kat, 0) + 1
    return jsonify({
        "pocet_receptov": pocet,
        "pocet_oblubenych": oblubene,
        "kategorie": kategorie
    })

@app.route('/api/vyhladat')
def api_vyhladat():
    query = request.args.get('q', '').lower()
    recepty = nacitaj()
    if query:
        vysledky = [r for r in recepty if query in r['nazov'].lower() or query in r['ingrediencie'].lower()]
    else:
        vysledky = recepty
    return jsonify(vysledky)

@app.route('/pridat', methods=['POST'])
def pridat():
    nazov = request.form['nazov']
    ingrediencie = request.form['ingrediencie']
    postup = request.form['postup']
    kategoria = request.form.get('kategoria', '')
    
    recepty = nacitaj()
    recepty.append({"nazov": nazov, "ingrediencie": ingrediencie, "postup": postup, "kategoria": kategoria})
    uloz(recepty)
    
    return redirect(url_for('index'))

@app.route('/zmazat/<int:index>', methods=['POST'])
def zmazat(index):
    recepty = nacitaj()
    if 0 <= index < len(recepty):
        del recepty[index]
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

@app.route('/toggle_favorite/<int:index>', methods=['POST'])
def toggle_favorite(index):
    recepty = nacitaj()
    if 0 <= index < len(recepty):
        if 'favorite' not in recepty[index]:
            recepty[index]['favorite'] = False
        recepty[index]['favorite'] = not recepty[index]['favorite']
        uloz(recepty)
        return jsonify({"favorite": recepty[index]['favorite']})
    return jsonify({"error": "Recept neexistuje"}), 404

@app.route('/favorites')
def favorites():
    recepty = nacitaj()
    oblubene = [r for r in recepty if r.get('favorite')]
    return render_template('index.html', recepty=oblubene, aktivna_kategoria='oblubene')

if __name__ == '__main__':
    app.run(debug=True)