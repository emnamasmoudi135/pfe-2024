# app/api/userManagement/auth.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request, jsonify, current_app as app
from app.api.userManagement.user import User
import jwt
import datetime

class Auth:
    @staticmethod
    def send_verification_email(email, token, subject, text):
        smtp_server = app.config['SMTP_SERVER']
        smtp_port = app.config['SMTP_PORT']
        smtp_username = app.config['SMTP_USERNAME']
        smtp_password = app.config['SMTP_PASSWORD']

        sender_email = smtp_username
        receiver_email = email

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        part = MIMEText(text, "plain")
        message.attach(part)

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
        except Exception as e:
            print(f"Error sending email: {e}")

    @staticmethod
    def signup():
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        user = User()
        success, message, token = user.create_user(username, email, password, role)
        if success:
            text = f"Please verify your email by clicking the following link: http://localhost:5000/verify-email?token={token}"
            Auth.send_verification_email(email, token, "Email Verification", text)
            return jsonify({"message": message}), 201
        return jsonify({"error": message}), 400

    @staticmethod
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User()
        user_data = user.find_user_by_email(email)
        if not user_data or not user.verify_password(user_data, password):
            return jsonify({"error": "Invalid email or password"}), 401

        if not user_data.get("is_email_verified"):
            return jsonify({"error": "Email not verified. Please check your email."}), 401
        
        verification_token = user.create_login_token(email)
        text = f"Please confirm your login by clicking the following link: http://localhost:5000/confirm-login?token={verification_token}"
        Auth.send_verification_email(email, verification_token, "Confirm Login", text)

        return jsonify({"message": "Please confirm your login via the email sent."}), 200

    @staticmethod
    def confirm_login():
        token = request.args.get('token')
        user = User()
        user_data = user.verify_login_token(token)
        if user_data:
            token = jwt.encode({
                'user_id': str(user_data['_id']),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({'token': token}), 200
        return jsonify({"error": "Invalid or expired login confirmation token."}), 400

    @staticmethod
    def verify_email():
        token = request.args.get('token')
        user = User()
        if user.verify_email(token):
            return jsonify({"message": "Email verified successfully."}), 200
        return jsonify({"error": "Invalid verification token."}), 400

    @staticmethod
    def logout():
        response = jsonify({"message": "Successfully logged out"})
        response.set_cookie('token', '', expires=0)  # Remove the token cookie
        return response, 200
