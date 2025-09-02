from flask import Flask, request, jsonify
import re
import smtplib
import dns.resolver
import socket

app = Flask(__name__)

# Simple email format validator
def is_valid_format(email):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email)

# Extract domain from email
def get_domain(email):
    return email.split('@')[-1]

# Verify email using SMTP
def verify_email_smtp(email):
    try:
        domain = get_domain(email)

        # Get MX records
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(sorted(records, key=lambda r: r.preference)[0].exchange)

        # SMTP conversation
        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)  # Turn on debug output if needed
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('you@example.com')  # Use any dummy sender
        code, message = server.rcpt(email)
        server.quit()

        # SMTP 250 means accepted
        return code == 250

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, socket.timeout, smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError):
        return False


@app.route('/validate-email', methods=['POST'])
def validate_email():
    data = request.get_json()
    email = data.get('email')

    if not email or not is_valid_format(email):
        return jsonify({'valid': False, 'reason': 'Invalid format'}), 400

    is_valid = verify_email_smtp(email)

    if is_valid:
        return jsonify({'valid': True}), 200
    else:
        return jsonify({'valid': False, 'reason': 'SMTP verification failed'}), 400


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)



if __name__ == '__main__':
    app.run(debug=True)
