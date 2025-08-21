import os
import json
import pdfplumber
from flask import Flask, request, render_template
from openai import OpenAI

app = Flask(__name__)

client = OpenAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    pdf_file = request.files.get('pdf')
    if not pdf_file:
        return "No PDF uploaded", 400

    with pdfplumber.open(pdf_file.stream) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=text,
        response_format={"type": "json_object"},
    )

    result_json = json.loads(response.output_text)
    return render_template('index.html', factura=result_json.get("factura", []))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
