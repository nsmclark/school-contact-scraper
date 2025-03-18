import os  
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# ✅ Root route to confirm app is running
@app.route("/", methods=["GET"])
def home():
    return "✅ School Contact Scraper is Running!"

# ✅ List of school faculty directory URLs
SCHOOLS = {
    "Asheville Christian Academy": "https://www.ashevillechristian.org/about-us/faculty-staff/",
    "Ben Lippen School": "https://www.benlippen.com/faculty-staff/",
    "Brentwood Academy": "https://www.brentwoodacademy.com/about/faculty-staff"
}

# ✅ Titles to search for
TARGET_TITLES = ["Head of School", "Headmaster", "Principal", "Director of Admissions", "Admissions Director", "Marketing Director", "Director of Marketing"]

# ✅ Function to extract contact details
def extract_contacts(school_name, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        return {"error": f"Error accessing {url}: {e}"}

    if response.status_code != 200:
        return {"error": f"Failed to access {url} - Status Code: {response.status_code}"}
    
    soup = BeautifulSoup(response.text, "html.parser")
    contacts = []

    for person in soup.find_all(["div", "li", "p", "tr"]):
        text = person.get_text(separator=" ").strip()
        email = None
        if "@" in text:
            words = text.split()
            for word in words:
                if "@" in word and "." in word:
                    email = word.strip()
                    break
        
        for title in TARGET_TITLES:
            if title.lower() in text.lower():
                name = text.split(title)[0].strip()
                contacts.append({
                    "School Name": school_name,
                    "Contact Name": name,
                    "Title": title,
                    "Email": email if email else "Not Found",
                    "Source Link": url
                })
                break

    return contacts

# ✅ Scraping route
@app.route("/scrape", methods=["GET"])
def scrape_schools():
    all_contacts = []
    for school, url in SCHOOLS.items():
        contacts = extract_contacts(school, url)
        all_contacts.extend(contacts)
        time.sleep(2)  # Delay to avoid blocking

    return jsonify(all_contacts)

# ✅ Ensure Render correctly uses the assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  
    app.run(host="0.0.0.0", port=port)

