import os
import threading
import time
import secrets
import logging
from flask import Flask, request, jsonify
from werkzeug.serving import make_server

logger = logging.getLogger(__name__)

from shop_bot.data_manager import remnawave_repository as rw_repo

class CaptchaService:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.site_key = rw_repo.get_setting("captcha_site_key") or "pk_demo_astracat_captcha_public"
        self.app = Flask(__name__)
        self.server = None
        self.thread = None
        self.token = None
        self.success = False

        @self.app.route('/captcha')
        def captcha_page():
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Captcha</title>
            </head>
            <body>
                <iframe src="https://astracaph.vercel.app/captcha/widget?siteKey={self.site_key}&theme=dark"
                        width="350" height="500" frameborder="0" scrolling="no"></iframe>
                <script>
                    window.addEventListener("message", (event) => {{
                        if (event.origin !== "https://astracaph.vercel.app") {{
                            return;
                        }}
                        if (event.data.type === 'astracaph-verified') {{
                            const {{ token, success }} = event.data.detail;
                            if (success) {{
                                fetch("/verify", {{
                                    method: "POST",
                                    headers: {{ "Content-Type": "application/json" }},
                                    body: JSON.stringify({{ token: token }}),
                                }});
                            }}
                        }}
                    }});
                </script>
            </body>
            </html>
            """

        @self.app.route('/verify', methods=['POST'])
        def verify():
            data = request.get_json()
            self.token = data.get('token')
            self.success = True
            return jsonify({{"success": True}})

    def run_server(self, port, expiration_time=40):
        self.server = make_server('0.0.0.0', port, self.app)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

        end_time = time.time() + expiration_time
        while time.time() < end_time and not self.success:
            time.sleep(1)

        self.server.shutdown()
        self.thread.join()

    def get_verification_token(self, port):
        self.success = False
        self.token = None

        self.run_server(port)

        return self.token

if __name__ == '__main__':
    # Example usage
    secret_key = os.environ.get("CAPTCHA_SECRET_KEY")
    if not secret_key:
        raise ValueError("CAPTCHA_SECRET_KEY environment variable not set")

    captcha_service = CaptchaService(secret_key=secret_key)

    port = 48392  # Example port
    print(f"Please go to http://127.0.0.1:{port}/captcha to solve the captcha.")

    token = captcha_service.get_verification_token(port)

    if token:
        print(f"Verification token received: {token}")
    else:
        print("Captcha not solved in time.")
