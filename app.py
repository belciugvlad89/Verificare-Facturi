import os
import json
import traceback
import pdfplumber
from flask import Flask, request, render_template, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        pdf_file = request.files.get('file')
        if not pdf_file:
            return jsonify({"error": "No PDF uploaded"}), 400

        with pdfplumber.open(pdf_file.stream) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        prompt = (
            "Extrage informațiile despre linii de factură din textul de mai jos "
            "și răspunde strict în format JSON conform schemei cerute. "
            f"{text}"
        )

        system_msg = (
            "Ești un extractor de date din facturi. "
            "Răspunzi STRICT ca obiect JSON (fără explicații, fără markdown). "
            'Schema: {"factura":[{"Denumire_Furnizor":string,"Denumire_Material":string,'
            '"Cantitate":number,"Pret_unitar":number,"Pret_total":number}]}'
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=800,
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content
        data = json.loads(content)
        return jsonify(data)
    except Exception as e:
        print("UPLOAD ERROR:", e)
        print(traceback.format_exc())
        return jsonify({"error": "Processing failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False)
