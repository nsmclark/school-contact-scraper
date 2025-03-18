from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def extract_emails(url):
    """Scrapes the given URL and extracts email addresses."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"error": f"Error accessing {url}: {response.status_code} {response.reason}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        emails = set()

        # Extract emails from <a href="mailto:EMAIL">
        for a_tag in soup.find_all('a', href=True):
            if 'mailto:' in a_tag['href']:
                email = a_tag['href'].replace('mailto:', '').strip()
                emails.add(email)

        # Extract emails from plain text
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        text_emails = re.findall(email_pattern, soup.get_text())
        emails.update(text_emails)

        # Debugging: Log scraped data
        print(f"Scraped from {url}: {emails}")

        if not emails:
            return {"error": f"No faculty contact details found on {url}"}
        
        return list(emails)

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@app.route('/scrape', methods=['POST'])
def scrape_faculty_contacts():
    """API endpoint to scrape faculty emails from provided URLs."""
    try:
        data = request.json
        if not data or 'urls' not in data:
            return jsonify({"error": "Missing 'urls' in request payload"}), 400
        
        urls = data['urls']
        results = {}

        for url in urls:
            results[url] = extract_emails(url)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
