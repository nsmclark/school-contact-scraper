import os  
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
import re

app = Flask(__name__)

# ✅ Root route to confirm app is running
@app.route("/", methods=["GET"])
def home():
    return "✅ School Contact Scraper is Running!"

# ✅ Titles to search for
TARGET_TITLES = [
    "Head of School", "Headmaster", "Principal", 
    "Director of Admissions", "Admissions Director", 
    "Marketing Director", "Director of Marketing"
]

# ✅ Extract faculty details properly
def extract_contacts(school_name, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return [{"error": f"Error accessing {url}: {e}"}]

    soup = BeautifulSoup(response.text, "html.parser")
    contacts = []

    # ✅ Search inside faculty directory containers
    faculty_sections = soup.find_all(["table", "ul", "ol", "div"], class_=lambda x: x and "staff" in x.lower())

    if not faculty_sections:
        faculty_sections = soup.find_all(["div", "p", "tr"])  # Fallback search

    for section in faculty_sections:
        for person in section.find_all(["tr", "li", "p", "div"]):  # Check inside rows or lists
            text = person.get_text(separator=" ").strip()

            # ✅ Extract email using regex
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
            email = email_match.group(0) if email_match else "Not Found"

            # ✅ Check if the person's title matches target roles
            for title in TARGET_TITLES:
                if title.lower() in text.lower():
                    name = text.split(title)[0].strip()
                    contacts.append({
                        "School Name": school_name,
                        "Contact Name": name,
                        "Title": title,
                        "Email": email,
                        "Source Link": url
                    })
                    break

    # ✅ If no contacts found, return an error
    if not contacts:
        contacts.append({"error": f"No valid faculty contacts found on {url}"})

    return contacts

# ✅ New Scraping Route That Accepts Dynamic Websites
@app.route("/scrape", methods=["POST"])
def scrape_schools():
    data = request.json  # Read JSON input from the GPT request
    if not data or "schools" not in data:
        return jsonify({"error": "Please provide a list of school names and URLs in JSON format."}), 400

    all_contacts = []
    for school in data["schools"]:  # Loop through user-provided schools
        name = school.get("name")
        url = school.get("url")

        if not name or not url:
            continue

        contacts = extract_contacts(name, url)
        all_contacts.extend(contacts)
        time.sleep(2)  # Delay to avoid blocking

    return jsonify(all_contacts)

# ✅ Ensure Render correctly uses the assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  
    app.run(host="0.0.0.0", port=port)

