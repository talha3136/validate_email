import smtplib
import dns.resolver
import socket
import re
from flask import Flask, request, jsonify
import smtplib, socket, dns.resolver

app = Flask(__name__)
def get_mx_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [r.exchange.to_text() for r in answers]
        # print(f"[INFO] MX records for {domain}: {mx_records}")
        return mx_records
    except Exception as e:
        print(f"[ERROR] Failed to get MX records for {domain}: {e}")
        return []

def is_valid_email_smtp(email):
    # Basic format check
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("[ERROR] Invalid email format.")
        return False

    domain = email.split('@')[1]
    mx_records = get_mx_records(domain)

    if not mx_records:
        print(f"[ERROR] No MX records found for {domain}")
        return False

    # Use the first MX record
    mail_server = mx_records[0]
    try:
        print(f"[INFO] Connecting to {mail_server}...")
        server = smtplib.SMTP(timeout=10)
        server.connect(mail_server)
        server.helo(socket.gethostname())
        server.mail("test@example.com")  # Dummy sender
        code, message = server.rcpt(email)
        server.quit()
        print(f"[INFO] Server response: {code} {message}")

        if code == 250:
            print(f"[VALID] {email} is valid.")
            return True
        else:
            print(f"[INVALID] {email} rejected by server. Code: {code}")
            return False
    except Exception as e:
        print(f"[ERROR] SMTP connection failed: {e}")
        return False
    
@app.route('/verify-email', methods=['POST'])
def verify():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    result = is_valid_email_smtp(email)
    return jsonify({"email": email, "valid": result})




if __name__ == '__main__':
    app.run(debug=True)
