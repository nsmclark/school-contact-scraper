import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape_faculty_contacts():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)

        # If blocked or error page
        if response.status_code != 200:
            return jsonify({"error": f"Request failed with status {response.status_code}"}), response.status_code
        
        soup = BeautifulSoup(response.text, 'html.parser')

        contacts = []

        # Try different possible structures (divs, tables, paragraphs)
        faculty_sections = soup.find_all(["div", "section", "table", "tr", "td", "p"])

        for section in faculty_sections:
            name = section.find(["h2", "h3", "strong", "b"])
            email = section.find("a", href=lambda href: href and "mailto:" in href)
            title = section.find(["span", "td", "p"], class_=lambda x: x and "title" in x.lower() or "position" in x.lower())

            if name and email:
                contacts.append({
                    "name": name.get_text(strip=True),
                    "email": email["href"].replace("mailto:", "").strip(),
                    "title": title.get_text(strip=True) if title else "Not Found",
                    "source": url
                })

        # Log errors instead of breaking the server
        if not contacts:
            return jsonify({"error": "No faculty contacts found"}), 404

        return jsonify(contacts)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
