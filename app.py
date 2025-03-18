import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define the faculty titles to search for
FACULTY_TITLES = [
    "Head of School", "Headmaster", "Principal", "Director of Admissions",
    "Admissions Director", "Marketing Director", "Director of Marketing"
]

def scrape_faculty_contacts(directory_url):
    """Scrapes the faculty directory page for contact names and emails."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(directory_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        faculty_list = []

        # Look for common patterns (tables, divs, spans, etc.)
        for item in soup.find_all(["tr", "div", "span", "li"]):
            text = item.get_text(separator=" ", strip=True)
            email = None

            # Extract email if present
            email_tag = item.find("a", href=True)
            if email_tag and "mailto:" in email_tag["href"]:
                email = email_tag["href"].replace("mailto:", "")

            # Check if any faculty title is mentioned
            if any(title.lower() in text.lower() for title in FACULTY_TITLES):
                faculty_list.append({
                    "Contact Name": text,
                    "Title": [title for title in FACULTY_TITLES if title.lower() in text.lower()],
                    "Email": email or "Not Found",
                    "Source Link": directory_url
                })

        return faculty_list if faculty_list else [{"error": f"No faculty contacts found on {directory_url}"}]

    except requests.exceptions.RequestException as e:
        return [{"error": f"Error accessing {directory_url}: {str(e)}"}]


@app.route("/scrape", methods=["POST"])
def scrape():
    """Receives a faculty directory URL and scrapes contact details."""
    data = request.json
    directory_url = data.get("directory_url")

    if not directory_url:
        return jsonify({"error": "No directory URL provided"}), 400

    result = scrape_faculty_contacts(directory_url)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
