import os
from base64 import b64encode

os.environ["BUY_URL"] = "http://"
os.environ["PAYPAL_CLIENT_ID"] = ""
os.environ["PAYPAL_CLIENT_SECRET"] = ""
os.environ["PAYPAL_WEBHOOK_ID"] = "40L71081MK3756722"
os.environ["PEPPER"] = b64encode(b"Red Hot Chili Peppers").decode()
os.environ["SENTRY_DSN_BACKEND"] = ""
os.environ["SENTRY_DSN_FRONTEND"] = ""
os.environ["SMTP_PASSWORD"] = ""
os.environ["STRIPE_API_KEY"] = ""
os.environ["STRIPE_WEBHOOK_SEC_KEY"] = "whsec_9xiTmKH5BPEaXtXZyWWGFljQS5emeJZ7"
