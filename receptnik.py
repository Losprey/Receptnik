import json
import os
import sys

SUBOR = "recepty.json"

def nacitaj():
    if not os.path.exists(SUBOR):
        return []
    with open(SUBOR, "r") as f:
        return json.load(f)

def uloz(recepty):
    with open(SUBOR, "w") as f:
        json.dump(recepty, f, ensure_ascii=False, indent=2)

def pridaj_recept():
    nazov = input("Názov receptu: ")
    ingrediencie = input("Ingrediencie (oddeľ čiarkou): ")
    postup = input("Postup: ")
    recepty = nacitaj()
    recepty.append({"nazov": nazov, "ingrediencie": ingrediencie, "postup": postup})
    uloz(recepty)
    print("✅ Recept uložený!")

def zobraz_recepty():
    recepty = nacitaj()
    if not recepty:
        print("Žiadne recepty.")
        return
    for i, r in enumerate(recepty, 1):
        print(f"\n{i}. {r['nazov']}")
        print(f"   Ingrediencie: {r['ingrediencie']}")
        print(f"   Postup: {r['postup']}")

def hladaj():
    ingrediencia = input("Zadaj ingredienciu: ").lower()
    recepty = nacitaj()
    najdene = [r for r in recepty if ingrediencia in r['ingrediencie'].lower()]
    if not najdene:
        print("Žiadne recepty s touto ingredienciou.")
    for r in najdene:
        print(f"\n✅ {r['nazov']}")
        print(f"   {r['ingrediencie']}")

def ai_navrh():
    ingrediencie = input("Čo máš doma? (oddeľ čiarkou): ")
    import subprocess
    import json as j
    data = j.dumps({"model":"deepseek-chat","messages":[{"role":"user","content":f"Navrhni jednoduchý recept z týchto ingrediencií: {ingrediencie}. Odpovedaj po slovensky."}]})
    result = subprocess.run(["curl","-s","https://api.deepseek.com/chat/completions","-H",f"Authorization: Bearer {os.environ['DEEPSEEK_API_KEY']}","-H","Content-Type: application/json","-d",data], capture_output=True, text=True)
    odpoved = j.loads(result.stdout)
    print("\n🤖 AI navrhuje:\n")
    print(odpoved["choices"][0]["message"]["content"])

while True:
    print("\n--- RECEPTNÍK ---")
    print("1. Pridať recept")
    print("2. Zobraziť recepty")
    print("3. Hľadať podľa ingrediencie")
    print("4. AI návrh receptu")
    print("5. Koniec")
    volba = input("\nVoľba: ")
    if volba == "1": pridaj_recept()
    elif volba == "2": zobraz_recepty()
    elif volba == "3": hladaj()
    elif volba == "4": ai_navrh()
    elif volba == "5": break
