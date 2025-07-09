import os
from datetime import timedelta
from pathlib import Path

PROJECT = "reader.dict"
WWW = "reader-dict.com"
PATREON = "https://www.patreon.com/mschoentgen"

HERE = Path(__file__).parent
ROOT = HERE.parent
ASSET = ROOT / "asset"
DATA = ROOT / "data"
DICTIONARIES = DATA / "dictionary.json"
FILES = ROOT / "file"
FILES_CACHE = ROOT / "cache"
CERTS = FILES / "certificates"
EMAILS = DATA / "emails"
LOGS = ROOT / "logs.log"
METRICS = DATA / "metrics.json"
ORDERS = DATA / "orders.json"
PURCHASE_FILES = FILES / "purchase"
VIEW = HERE / "view"

DICTIONARY_KEYS = ["formats", "name", "plan_id", "price", "price_purchase", "progress", "updated", "words"]

# The order is important, and will be reflected on the website.
# It might be good to sort based on download counts when we'll have metrics.
DICTIONARY_FORMATS = {
    "kobo": ("Kobo", "dicthtml-{lang_src}-{lang_dst}{etym_suffix}.zip"),
    "mobi": ("Kindle", "dict-{lang_src}-{lang_dst}{etym_suffix}.mobi.zip"),
    "stardict": ("StarDict", "dict-{lang_src}-{lang_dst}{etym_suffix}.zip"),
    "df": ("DictFile", "dict-{lang_src}-{lang_dst}{etym_suffix}.df.bz2"),
    "dictorg": ("DICT.org", "dictorg-{lang_src}-{lang_dst}{etym_suffix}.zip"),
}

# Download links availability
DELAY_BEFORE_EXPIRATION_IN_SEC = 10 * 60

HOST = "0.0.0.0"  # noqa: S104
SERVER = "wsgiref"
PORT = 1024

HTTP_HEADERS = {"User-Agent": f"www.{WWW}"}
GITHUB_API_TRACKER = "https://api.github.com/repos/reader-dict/report-a-word/issues"
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
GITHUB_URL_TRACKER = "https://github.com/reader-dict/report-a-word"
PAYPAL_URL_PLAN = "https://api-m.paypal.com/v1/billing/plans"
PAYPAL_URL_PRICE = "https://api-m.paypal.com/v1/billing/plans/{0}/update-pricing-schemes"
PAYPAL_URL_PURCHASES = "https://api.paypal.com/v2/checkout/orders/{0}"
PAYPAL_URL_PURCHASE_REFUND = "https://api.paypal.com/v2/payments/captures/{0}/refund"
PAYPAL_URL_SUBSCRIPTIONS = "https://api.paypal.com/v1/billing/subscriptions/{0}"
PAYPAL_URL_TOKEN = "https://api-m.paypal.com/v1/oauth2/token"  # noqa: S105
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID", "")

# GlitchTip for errors reporting
SENTRY_DSN_BACKEND = os.getenv("SENTRY_DSN_BACKEND", "")
SENTRY_DSN_FRONTEND = os.getenv("SENTRY_DSN_FRONTEND", "")
SENTRY_ENV_DEV = "development"
SENTRY_ENV_PROD = "production"

# SMPT stuff
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

PEPPER = os.getenv("PEPPER", "")

ONE_MONTH = timedelta(days=365.25 / 12)
EXPIRED = timedelta()

# HTML metatags
KEYWORDS = "kobo,kindle,onyx boox,pocketbook,dict.org,dictorg,dictfile,dicthtml,mobi,stardict,koreader,goldendict,plato,colordict,flowdict"  # noqa: E501

PRICE_LEVELS = [
    range(1, 500),
    range(500, 1_000),
    range(1_000, 10_000),
    range(10_000, 100_000),
    range(100_000, 1_000_000),
    range(1_000_000, 2_000_000),
    range(2_000_000, 3_000_000),
    range(3_000_000, 4_000_000),
    range(4_000_000, 5_000_000),
    range(5_000_000, 6_000_000),
    range(6_000_000, 7_000_000),
    range(7_000_000, 8_000_000),
]

# Routes
ROUTE_API_DICT = "/api/v1/dictionaries"
ROUTE_API_ORDER = "/api/v1/order"
ROUTE_API_WEBHOOK_PAYPAL = "/api/v1/webhook/paypal"

PAYPAL_EVENT_PURCHASE_APPROVED = "CHECKOUT.ORDER.APPROVED"
PAYPAL_EVENT_PURCHASE_COMPLETED = "PAYMENT.CAPTURE.COMPLETED"
PAYPAL_EVENT_PURCHASE_REFUNDED = "PAYMENT.CAPTURE.REFUNDED"
PAYPAL_EVENT_SUBSCRIPTION_CANCELLED = "BILLING.SUBSCRIPTION.CANCELLED"
PAYPAL_EVENT_SUBSCRIPTION_COMPLETED = "PAYMENT.SALE.COMPLETED"
PAYPAL_EVENT_SUBSCRIPTION_CREATED = "BILLING.SUBSCRIPTION.CREATED"
PAYPAL_EVENT_SUBSCRIPTION_SUSPENDED = "BILLING.SUBSCRIPTION.SUSPENDED"
