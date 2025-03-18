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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch the webpage. Status code: {response.status_code}"}), 400

        soup = BeautifulSoup(response.text, 'html.parser')

        faculty_list = []

        # Search for relevant elements in a safer way
        for tag in soup.find_all(['p', 'div', 'span', 'a', 'li']):
            text = tag.get_text(strip=True) if tag else None

            if text:
                # Check if the tag contains relevant faculty/staff information
                if any(keyword in text.lower() for keyword in ["head of school", "principal", "director of admissions", "marketing director"]):
                    email = None
                    
                    # Try to extract email from <a> tag (if present)
                    email_tag = tag.find('a', href=True)
                    if email_tag and "mailto:" in email_tag['href']:
                        email = email_tag['href'].replace("mailto:", "")

                    faculty_list.append({
                        "Name": text,
                        "Email": email if email else "Not Found",
                        "Source": url
                    })

        # If no faculty contacts were found
        if not faculty_list:
            return jsonify({"error": "No faculty contact details found on the page"}), 404

        return jsonify(faculty_list)

    except requests.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
