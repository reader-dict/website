import os
from base64 import b64decode
from datetime import timedelta
from pathlib import Path

PROJECT = "reader.dict"
WWW = "reader-dict.com"

HERE = Path(__file__).parent
ROOT = HERE.parent
ASSET = ROOT / "asset"
DATA = ROOT / "data"
DICTIONARIES = DATA / "dictionary.json"
REVIEWS = DATA / "reviews.json"
FAQ = ASSET / "faq.json"
FILES = ROOT / "file"
FILES_CACHE = ROOT / "cache"
CERTS = FILES / "certificates"
EMAILS = DATA / "emails"
LOGS = ROOT / "logs.log"
METRICS = DATA / "metrics.json"
ORDERS = DATA / "orders.json"
SPONSORS = DATA / "sponsors.json"
VIEW = HERE / "view"

DICTIONARY_KEYS_MINIMAL = ["formats", "updated", "words"]
DICTIONARY_KEYS_DOWNLOAD = [*DICTIONARY_KEYS_MINIMAL, "name"]
DICTIONARY_KEYS_ALL = [
    *DICTIONARY_KEYS_DOWNLOAD,
    "plan_id",
    "price",
    "price_purchase",
    "progress",
]

# The order is important, and will be reflected on the website.
DICTIONARY_FORMATS = {
    "stardict": ("StarDict", "dict-{lang_src}-{lang_dst}{etym_suffix}.zip"),
    "kobo": ("Kobo", "dicthtml-{lang_src}-{lang_dst}{etym_suffix}.zip"),
    "mobi": ("Kindle", "dict-{lang_src}-{lang_dst}{etym_suffix}.mobi.zip"),
    "dictorg": ("DICT.org", "dictorg-{lang_src}-{lang_dst}{etym_suffix}.zip"),
    "df": ("DictFile", "dict-{lang_src}-{lang_dst}{etym_suffix}.df.bz2"),
}

# Download links availability
DELAY_BEFORE_EXPIRATION_IN_SEC = 10 * 60

HOST = "0.0.0.0"  # noqa: S104
SERVER = "wsgiref"
PORT = 1024
HEADER_SLOGAN = "Best Dictionaries for Your Beloved e-Reader"
HEADER_SLOGAN_SPLIT = "Best Dictionaries<br>for Your Beloved e-Reader"
HEADER_DESC = "The most comprehensive universal, multilingual, and monolingual dictionaries—perfect for e-readers, phones, tablets, and desktop apps. Powered by Wiktionary. Updates at least twice a month and support for over 180 languages. Compatible with Kindle, Kobo, Onyx Boox, PocketBook, and more."  # noqa: E501
HEADER_DESC_HTML = 'The most comprehensive universal, multilingual, and monolingual dictionaries—perfect for e-readers, phones, tablets, and desktop apps. Powered by <a href="https://www.wiktionary.org/" target="_blank" rel="noopener noreferrer" class="external underline">Wiktionary</a>.<br>Updates at least twice a month and support for over 180 languages.'  # noqa: E501

HTTP_HEADERS = {"User-Agent": f"www.{WWW}"}
GITHUB_API_TRACKER = "https://api.github.com/repos/reader-dict/report-a-word/issues"
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")
GITHUB_URL = "https://github.com/reader-dict"
GOOGLE_REVIEWS = "https://g.page/r/CZpXIafh6L0VEBI/review"
PAYPAL_CLIENT_ID = os.environ["PAYPAL_CLIENT_ID"]
PAYPAL_CLIENT_SECRET = os.environ["PAYPAL_CLIENT_SECRET"]
PAYPAL_URL_PURCHASES = "https://api.paypal.com/v2/checkout/orders/{0}"
PAYPAL_URL_PURCHASE_REFUND = "https://api.paypal.com/v2/payments/captures/{0}/refund"
PAYPAL_URL_SUBSCRIPTIONS = "https://api.paypal.com/v1/billing/subscriptions/{0}"
PAYPAL_URL_TOKEN = "https://api-m.paypal.com/v1/oauth2/token"  # noqa: S105
PAYPAL_WEBHOOK_ID = os.environ["PAYPAL_WEBHOOK_ID"]
STRIPE_API_KEY = os.environ["STRIPE_API_KEY"]
STRIPE_URL_CHECKOUT_SESSION = "https://api.stripe.com/v1/checkout/sessions"
STRIPE_WEBHOOK_SEC_KEY = os.environ["STRIPE_WEBHOOK_SEC_KEY"]

# GlitchTip for errors reporting
SENTRY_DSN_BACKEND = os.environ["SENTRY_DSN_BACKEND"]

# SMPT stuff
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

# The pepper is base64-encoded to prevent UTF-8 mess on how an envar can be stored on the host provider
PEPPER = b64decode(os.environ["PEPPER"]).decode()

ONE_MONTH = timedelta(days=365.25 / 12)
EXPIRED = timedelta()

PRICE = 9.49  # Sync with STRIPE_PRICE_ID
PRICE_HTML = "9<span>.49</span>"
STRIPE_PRICE_ID = os.environ["STRIPE_PRICE_ID"]

# Routes
ROUTE_API_DICT = "/api/v1/dictionaries"
ROUTE_API_PRE_ORDER = "/api/v1/pre-order"
ROUTE_API_WEBHOOK = "/api/v1/webhook/<source>"
ROUTE_API_WEBHOOK_PAYPAL = "/api/v1/webhook/paypal"
ROUTE_API_WEBHOOK_STRIPE = "/api/v1/webhook/stripe"

PAYPAL_EVENT_PURCHASE_APPROVED = "CHECKOUT.ORDER.APPROVED"
PAYPAL_EVENT_PURCHASE_COMPLETED = "PAYMENT.CAPTURE.COMPLETED"
PAYPAL_EVENT_PURCHASE_REFUNDED = "PAYMENT.CAPTURE.REFUNDED"
PAYPAL_EVENT_SUBSCRIPTION_CANCELLED = "BILLING.SUBSCRIPTION.CANCELLED"
PAYPAL_EVENT_SUBSCRIPTION_COMPLETED = "PAYMENT.SALE.COMPLETED"
PAYPAL_EVENT_SUBSCRIPTION_CREATED = "BILLING.SUBSCRIPTION.CREATED"
PAYPAL_EVENT_SUBSCRIPTION_SUSPENDED = "BILLING.SUBSCRIPTION.SUSPENDED"

STRIPE_EVENT_PURCHASE_COMPLETED = "checkout.session.completed"
STRIPE_EVENT_PURCHASE_REFUNDED = "charge.refunded"

# Email content
EMAIL_BODY_HTML = """<html>
<head></head>
<body>
    <p><u><b>Thank you</b></u> for your trust, {0}!</p>
    <p>
        Here is the link to the dictionary files, which you should keep aside:
        <br/>
        <a href="{1}">{1}</a>
    </p>
    <p>
        Enjoy your reading,
        <br/>
        <br/>
        Mickaël.
    </p>
    <p>
        <hr/>
        {2}
        <br/>
        <a href="{3}">{3}</a>
    </p>
</body>
</html>
"""
EMAIL_BODY_TXT = """Thank you for your trust, {0}!

Here is the link to the dictionary files, which you should keep aside:

    {1}


Enjoy your reading,

Mickaël.

--
{2}
{3}
"""
EMAIL_SUBJECT = "📚 Your {0} dictionary"

# Needed for the VPS that uses ASCII by default (to revisit when moving to Python 3.13)
ENCODING = "utf-8"

# Dictionaries with less than this count of words are disabled
MINIMUM_REQUIRED_WORDS = 100
