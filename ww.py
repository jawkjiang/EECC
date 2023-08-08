from flask import Flask, request, jsonify
import json
import requests
import apikey
import csv

app = Flask(__name__)

# Replace with your actual OpenAI API key
OPENAI_API_KEY = "sk-L8F97XOcGHYcjC5GOMssbhlApyf3kseQBsF9Qy42PGqi32bR"

# Endpoint for the content curation API
@app.route('/curate', methods=['POST'])
def curate_content():
    try:
        data = request.get_json()

        curation_methods = data.get('curation_methods', '')
        content_to_curate = data.get('content_to_curate', '')

        curated_output = process_content(content_to_curate, curation_methods)

        return jsonify({"curated_result": curated_output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_content(content, curation_methods):
    prompt = f"Content Curation:\nCuration Methods:\n{curation_methods}\nContent to Curate:\n{content}"

    endpoint = 'https://api.closeai-proxy.xyz/v1'

    data = {
        'prompt': prompt,
        'max_tokens': 200
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    response = requests.post(endpoint, json=data, headers=headers)
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        curated_result = response_data['choices'][0]['text']
        return curated_result
    else:
        return "Error processing content"

if __name__ == '__main__':
    app.run(debug=True)