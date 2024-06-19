import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request, jsonify, redirect, current_app as app
from app.api.userManagement.user import User
from flask_jwt_extended import create_access_token, unset_jwt_cookies
import datetime
import uuid

class Auth:
    @staticmethod
    def send_email(email, subject, html_content):
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

        part2 = MIMEText(html_content, "html")
        message.attach(part2)

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
            verification_link = f"http://127.0.0.1:5000/verify-email?token={token}"
            html_content = f"""
            <html>
            <body>
                <p>Please confirm your email by clicking the following link:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
            </body>
            </html>
            """
            Auth.send_email(email, "Email Verification", html_content)
            return jsonify({"message": message}), 201
        return jsonify({"error": message}), 400

    @staticmethod
    def confirm_login():
        token = request.args.get('token')
        user = User()
        user_data = user.verify_login_token(token)
        if user_data:
            jwt_token = create_access_token(identity={"user_id": str(user_data['_id']), "role": user_data['role']})
            return redirect(f"http://127.0.0.1:3000/dashboard?token={jwt_token}")
        return jsonify({"error": "Invalid or expired login confirmation token."}), 400

    @staticmethod
    def verify_email():
        token = request.args.get('token')
        user = User()
        if user.verify_email(token):
            return jsonify({"message": "Email verified successfully."}), 200
        return jsonify({"error": "Invalid verification token."}), 400

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

        jwt_token = create_access_token(identity={"user_id": str(user_data['_id']), "role": user_data['role']})
        verification_link = f"http://127.0.0.1:3000/auth/login?token={jwt_token}"
        html_content = f"""
        <html>
        <body>
            <p>Please confirm your login by clicking the following link:</p>
            <p><a href="{verification_link}">I confirm that this is my account</a></p>
        </body>
        </html>
        """
        Auth.send_email(email, "Confirm Login", html_content)

        return jsonify({"message": "Please confirm your login via the email sent."}), 200

    @staticmethod
    def logout():
        response = jsonify({"message": "Successfully logged out"})
        unset_jwt_cookies(response)
        return response, 200

    @staticmethod
    def forgot_password():
        data = request.get_json()
        email = data.get('email')
        user = User()
        user_data = user.find_user_by_email(email)
        if not user_data:
            return jsonify({"error": "User with this email does not exist."}), 404

        reset_token = str(uuid.uuid4())
        reset_link = f"http://127.0.0.1:3000/auth/reset-password?token={reset_token}"
        user.save_reset_token(email, reset_token)
        
        html_content = f"""
        <html>
        <body>
            <p>Click the following link to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
        </body>
        </html>
        """
        Auth.send_email(email, "Reset Password", html_content)
        return jsonify({"message": "Password reset link has been sent to your email."}), 200

    @staticmethod
    def reset_password():
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        user = User()
        email = user.verify_reset_token(token)
        if not email:
            return jsonify({"error": "Invalid or expired reset token."}), 400

        user.update_password(email, new_password)
        return jsonify({"message": "Password has been reset successfully."}), 200
