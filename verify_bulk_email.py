import dns.resolver
import smtplib
import re

def get_mx_records(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_records = [record.exchange.to_text() for record in records]
        return mx_records
    except Exception as e:
        print(f"Failed to get MX records for domain {domain}: {e}")
        return []

def verify_email(email):
    # Regular expression to validate email format
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not email_regex.match(email):
        return False, "Invalid email format"

    domain = email.split('@')[1]
    mx_records = get_mx_records(domain)
    if not mx_records:
        return False, f"No MX records found for domain {domain}"

    # Connect to the first MX server
    mx_server = mx_records[0]
    try:
        server = smtplib.SMTP(mx_server)
        server.set_debuglevel(0)
        server.helo(server.local_hostname)  # Identify ourselves to the SMTP server
        server.mail('test@example.com')     # Mail from
        code, message = server.rcpt(email)  # RCPT TO
        server.quit()

        if code == 250:
            return True, "Valid email address"
        else:
            return False, f"Invalid email address: {message}"
    except Exception as e:
        return False, f"Failed to verify email address: {e}"

def verify_bulk_emails(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            email = line.strip()
            if email:
                is_valid, message = verify_email(email)
                result = f"{email}: {'Valid' if is_valid else 'Invalid'} - {message}\n"
                print(result.strip())
                outfile.write(result)

# Example usage
input_file = 'emails.txt'  # Path to the input file containing email addresses
output_file = 'results.txt'  # Path to the output file to save results
verify_bulk_emails(input_file, output_file)