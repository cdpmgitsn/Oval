import smtplib
from email.mime.text import MIMEText
import random
import string
import secrets


def pin_generator(length: int):
    chars = "abcdefghijklmnopqrstuvwxvzABCDEFGHIJKLMNOPQRSTUVWXVZ0123456789"

    real_pas = ''

    for item in range(length):
        pas_char = random.choice(chars)
        real_pas += pas_char

    return real_pas


def generate_mixed_hash():
    # Combine digits and letters (26 characters)
    characters = string.ascii_lowercase

    # Generate 26 random letters
    random_letters = ''.join(secrets.choice(characters) for _ in range(26))

    # Insert 8 random digits at random positions
    for _ in range(8):
        position = secrets.randbelow(34)
        random_letters = random_letters[:position] + secrets.choice(string.digits) + random_letters[position:]

    return random_letters


def email_msg(code: str):
    text = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Verification</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}

                    h2 {{
                        color: #333;
                    }}

                    p {{
                        color: #555;
                    }}

                    .reset-code {{
                        background-color: #fff;
                        border-radius: 5px;
                        padding: 20px;
                        text-align: center;
                    }}

                    .code {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #007bff;
                    }}
                    
                    .security-note {{
                        margin-top: 20px;
                        color: #888;
                    }}
                </style>
            </head>
            <body>
                <h2>Password Reset</h2>
                <p>We received a request to reset your password. Please use the following reset code:</p>
                <div class="reset-code">
                    <p class="code">{code}</p>
                </div>
                <p>If you did not request a password reset, please ignore this email.</p>
                <p class="security-note">For your security, do not share this reset code with anyone. This code is intended for your use only.</p>
            </body>
        </html>
        """
    return text


def send_new_password(code: str, reciever: str):
    sender = 'ovaluzb@gmail.com'
    password = 'ovdb nlct hmeq xcgr'

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    text = email_msg(code)

    try:
        server.login(sender, password)
        msg = MIMEText(text, "html")
        msg["From"] = sender
        msg["To"] = reciever
        msg["Subject"] = "Your new password for Oval is here"
        server.sendmail(sender, reciever, msg.as_string())
        print(1)
        return "The message was sent successfully!"
    except Exception as _ex:
        print(_ex)
        return f"{_ex} Check your login or password please!"


def are_decimal_digits_zero(number):
    # Check if the number is an integer or if the decimal part is all zeros
    return int(number) == number or int(number * 10**10) == int(number) * 10**10
