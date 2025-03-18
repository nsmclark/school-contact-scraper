import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])  # Explicitly allowing GET requests
def scrape_faculty_contacts():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}  # Prevents bot detection
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an error for bad responses (404, 500, etc.)

        soup = BeautifulSoup(response.text, 'html.parser')

        contacts = []

        # Searching for faculty/staff contacts
        for person in soup.find_all(["div", "p", "tr", "td"], class_=lambda x: x and "faculty" in x.lower() or "staff" in x.lower()):
            name = person.find(["h2", "h3", "strong", "b"])
            email = person.find("a", href=lambda href: href and "mailto:" in href)
            title = person.find(["p", "span", "td"], class_=lambda x: x and "title" in x.lower() or "position" in x.lower())

            if name and email:
                contacts.append({
                    "name": name.text.strip(),
                    "email": email["href"].replace("mailto:", "").strip(),
                    "title": title.text.strip() if title else "Not Found",
                    "source": url
                })

        if not contacts:
            return jsonify({"error": "No faculty contacts found"}), 404

        return jsonify(contacts)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error accessing {url}: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Uses correct Render port
