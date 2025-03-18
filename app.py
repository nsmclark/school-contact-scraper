import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape faculty/staff directory
def scrape_faculty_directory(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"Error accessing {url}: {response.status_code} {response.reason}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')

        faculty_list = []
        for element in soup.find_all(["p", "div", "li", "span", "tr"]):
            text = element.get_text(separator=" ", strip=True)
            
            if text and ("@" in text and "." in text):  # Detect emails in text
                parts = text.split()
                email = next((word for word in parts if "@" in word and "." in word), "Not Found")
                name = " ".join(parts[:2]) if len(parts) > 2 else "Not Found"
                title = " ".join(parts[2:]) if len(parts) > 3 else "Not Found"

                faculty_list.append({
                    "Contact Name": name,
                    "Title": title,
                    "Email": email,
                    "Source Link": url
                })
        
        if not faculty_list:
            return {"error": f"No faculty contact details found on {url}"}
        
        return faculty_list

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# API Endpoint to scrape multiple URLs
@app.route('/scrape', methods=['POST'])
def scrape_multiple():
    try:
        data = request.get_json()
        urls = data.get("urls", [])

        if not urls or not isinstance(urls, list):
            return jsonify({"error": "Invalid or missing 'urls' parameter. Must be a list of URLs."}), 400
        
        results = []
        for url in urls:
            result = scrape_faculty_directory(url)
            results.append(result)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500

# Run the app with the correct port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT if available
    app.run(host='0.0.0.0', port=port)
