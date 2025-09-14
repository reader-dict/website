import json

from src import constants, models

GITHUB_ISSUE = {
    "url": "https://api.github.com/repos/reader-dict/report-a-word/issues/1",
    "repository_url": "https://api.github.com/repos/reader-dict/report-a-word",
    "labels_url": "https://api.github.com/repos/reader-dict/report-a-word/issues/1/labels{/name}",
    "comments_url": "https://api.github.com/repos/reader-dict/report-a-word/issues/1/comments",
    "events_url": "https://api.github.com/repos/reader-dict/report-a-word/issues/1/events",
    "html_url": "https://github.com/reader-dict/report-a-word/issues/1",
    "id": 3107464249,
    "node_id": "I_kwDOO0Ly3s65OCQ5",
    "number": 1,
    "title": "[ES-EN] soportaba",
    "user": {
        "login": "BoboTiG",
        "id": 2033598,
        "node_id": "MDQ6VXNlcjIwMzM1OTg=",
        "avatar_url": "https://avatars.githubusercontent.com/u/2033598?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/BoboTiG",
        "html_url": "https://github.com/BoboTiG",
        "followers_url": "https://api.github.com/users/BoboTiG/followers",
        "following_url": "https://api.github.com/users/BoboTiG/following{/other_user}",
        "gists_url": "https://api.github.com/users/BoboTiG/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/BoboTiG/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/BoboTiG/subscriptions",
        "organizations_url": "https://api.github.com/users/BoboTiG/orgs",
        "repos_url": "https://api.github.com/users/BoboTiG/repos",
        "events_url": "https://api.github.com/users/BoboTiG/events{/privacy}",
        "received_events_url": "https://api.github.com/users/BoboTiG/received_events",
        "type": "User",
        "user_view_type": "public",
        "site_admin": False,
    },
    "labels": [
        {
            "id": 8710560482,
            "node_id": "LA_kwDOO0Ly3s8AAAACBzCa4g",
            "url": "https://api.github.com/repos/reader-dict/report-a-word/labels/English",
            "name": "English",
            "color": "34495E",
            "default": False,
            "description": "",
        },
        {
            "id": 8710756471,
            "node_id": "LA_kwDOO0Ly3s8AAAACBzOYdw",
            "url": "https://api.github.com/repos/reader-dict/report-a-word/labels/triage",
            "name": "triage",
            "color": "1D76DB",
            "default": False,
            "description": "The issue needs to be checked.",
        },
        {
            "id": 8710862181,
            "node_id": "LA_kwDOO0Ly3s8AAAACBzU1ZQ",
            "url": "https://api.github.com/repos/reader-dict/report-a-word/labels/feedback",
            "name": "feedback",
            "color": "ededed",
            "default": False,
            "description": None,
        },
    ],
    "state": "open",
    "locked": False,
    "assignee": None,
    "assignees": [],
    "milestone": None,
    "comments": 0,
    "created_at": "2025-06-01T16:03:32Z",
    "updated_at": "2025-06-01T16:03:32Z",
    "closed_at": None,
    "author_association": "OWNER",
    "active_lock_reason": None,
    "sub_issues_summary": {"total": 0, "completed": 0, "percent_completed": 0},
    "body": "👀 [soportaba](https://en.wiktionary.org/wiki/soportaba)",
    "closed_by": None,
    "reactions": {
        "url": "https://api.github.com/repos/reader-dict/report-a-word/issues/1/reactions",
        "total_count": 0,
        "+1": 0,
        "-1": 0,
        "laugh": 0,
        "hooray": 0,
        "confused": 0,
        "heart": 0,
        "rocket": 0,
        "eyes": 0,
    },
    "timeline_url": "https://api.github.com/repos/reader-dict/report-a-word/issues/1/timeline",
    "performed_via_github_app": None,
    "state_reason": None,
}
GITHUB_ISSUE_URL = "https://github.com/reader-dict/report-a-word/issues/1"

PAYPAL_CERT = """
-----BEGIN CERTIFICATE-----
MIIHXTCCBkWgAwIBAgIQDki0JdJMoAIx2jGAwTcTiTANBgkqhkiG9w0BAQsFADB1
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMTQwMgYDVQQDEytEaWdpQ2VydCBTSEEyIEV4dGVuZGVk
IFZhbGlkYXRpb24gU2VydmVyIENBMB4XDTI1MDEzMTAwMDAwMFoXDTI2MDMwMzIz
NTk1OVowgdsxEzARBgsrBgEEAYI3PAIBAxMCVVMxGTAXBgsrBgEEAYI3PAIBAhMI
RGVsYXdhcmUxHTAbBgNVBA8MFFByaXZhdGUgT3JnYW5pemF0aW9uMRAwDgYDVQQF
EwczMDE0MjY3MQswCQYDVQQGEwJVUzETMBEGA1UECBMKQ2FsaWZvcm5pYTERMA8G
A1UEBxMIU2FuIEpvc2UxFTATBgNVBAoTDFBheVBhbCwgSW5jLjEsMCoGA1UEAxMj
bWVzc2FnZXZlcmlmaWNhdGlvbmNlcnRzLnBheXBhbC5jb20wggEiMA0GCSqGSIb3
DQEBAQUAA4IBDwAwggEKAoIBAQCKsBDJSiEyFRDXhgYqSqGcRSlZ44O7iVHNjd3P
QiBc00kI4YwT4bZIGEa08QGRB+5xRLQDtmvTnQkz60YOFxwPaSZVdUEjybUCbbTu
TNJ117mK2V6G3KrMsXo4OZIv/oG8ayf9T6+ocRFB4s1IDHGGZJcbjgFjkq+5+3+N
aLATY9RHF3/qkq2RMFxCPqVQ/LSFdsEdkN4Q6FKWMYPTlScdTP1dg2YY6RdBXABP
M6DFEC0c+plO0RG4UsrATsnLQ0b4gN2cTb4JOwZaJsG2BSlpQCJWoX4gCP3Pkl2I
eLxjpaUDsfkdOMY78kUugZ60CPu29WYHlrLCBs5tSJ+rCHYxAgMBAAGjggOAMIID
fDAfBgNVHSMEGDAWgBQ901Cl1qCt7vNKYApl0yHU+PjWDzAdBgNVHQ4EFgQUIeCu
2GrxDXFuVkmB3JWC2psKP7swLgYDVR0RBCcwJYIjbWVzc2FnZXZlcmlmaWNhdGlv
bmNlcnRzLnBheXBhbC5jb20wSgYDVR0gBEMwQTALBglghkgBhv1sAgEwMgYFZ4EM
AQEwKTAnBggrBgEFBQcCARYbaHR0cDovL3d3dy5kaWdpY2VydC5jb20vQ1BTMA4G
A1UdDwEB/wQEAwIFoDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwdQYD
VR0fBG4wbDA0oDKgMIYuaHR0cDovL2NybDMuZGlnaWNlcnQuY29tL3NoYTItZXYt
c2VydmVyLWczLmNybDA0oDKgMIYuaHR0cDovL2NybDQuZGlnaWNlcnQuY29tL3No
YTItZXYtc2VydmVyLWczLmNybDCBiAYIKwYBBQUHAQEEfDB6MCQGCCsGAQUFBzAB
hhhodHRwOi8vb2NzcC5kaWdpY2VydC5jb20wUgYIKwYBBQUHMAKGRmh0dHA6Ly9j
YWNlcnRzLmRpZ2ljZXJ0LmNvbS9EaWdpQ2VydFNIQTJFeHRlbmRlZFZhbGlkYXRp
b25TZXJ2ZXJDQS5jcnQwDAYDVR0TAQH/BAIwADCCAX0GCisGAQQB1nkCBAIEggFt
BIIBaQFnAHYADleUvPOuqT4zGyyZB7P3kN+bwj1xMiXdIaklrGHFTiEAAAGUu81a
zwAABAMARzBFAiEA4FRk0fnMLk50tTYCr1yXMwBDP1/7VZ/8xAALIYpW7WwCICYM
e99wI7JAzkzMyzoqwJm5/vFOrb1VKQqpyWpFHquKAHYAZBHEbKQS7KeJHKICLgC8
q08oB9QeNSer6v7VA8l9zfAAAAGUu81a9gAABAMARzBFAiEA217qTUrcveLoXTGe
LeI8glW2dalUr2GzbPnfwycRE4wCIAXNh7RdTW50P2zHQGkmak7NYJ7ZxvPBkiNj
Fz2RGtY9AHUASZybad4dfOz8Nt7Nh2SmuFuvCoeAGdFVUvvp6ynd+MMAAAGUu81b
DQAABAMARjBEAiA0YxvSEpLzpohHg6zH1RC15xXTYn0Ik2SZ+R+v1XRScgIgfo5x
Og2qNi101qUvcuYUl9fFFol2aurZ/K23bWWUr50wDQYJKoZIhvcNAQELBQADggEB
AJDE7+ZogRtnY/SyNPOQDKSoowrDN6PE8eVXf2AIROyMdayOIaX74FRf2bTrUxIc
J3Dkdk1aFY/sqCq52ACB15iBAiDvamS4XuYYy0mbbZX8iQeQ0uvuPA/D2sH4gpEv
sBHHcLTfmkxL3BUTRh0JaTWhuGY9OSf5Vtl+Vt6JKEARw8br7SSc0SIz03NH9aKc
S3fVuCsbw1tbiqMtBHgPJ60EHWbbWzae9bqFPfTCAXvDpCi33vj4l1Am6i0kOmp4
2/CV4XomE/7JPPm+5odijca0+/6jQpVg9z/W12mOn08ykrL7lS7IpaSjiC3xMeeR
DMCtxZDITPKCPnbzgzl2Q/I=
-----END CERTIFICATE-----
"""
PAYPAL_CERT_URL = "https://api.paypal.com/v1/notifications/certs/CERT-360caa42-fca2a594-b0d12406"

STATUS_UPDATE_TIME = "2025-03-30T19:59:05+00:00"

PURCHASE_ID = "4Y574543DL4671844"
PURCHASE_DATA = {
    "id": PURCHASE_ID,
    "intent": "CAPTURE",
    "status": "COMPLETED",
    "payment_source": {
        "paypal": {
            "email_address": "alice@example.org",
            "account_id": "account-id",
            "account_status": "VERIFIED",
            "name": {"given_name": "Alice", "surname": "Dupont"},
            "address": {"country_code": "FR"},
        }
    },
    "purchase_units": [
        {
            "reference_id": "default",
            "amount": {
                "currency_code": "EUR",
                "value": "3.49",
                "breakdown": {"item_total": {"currency_code": "EUR", "value": "3.49"}},
            },
            "payee": {
                "email_address": "me@me.me",
                "merchant_id": "merchant-id",
                "display_data": {"brand_name": constants.PROJECT},
            },
            "soft_descriptor": "PAYPAL *READERDICT",
            "items": [
                {
                    "name": f"{constants.PROJECT} EO-FR (bilingual)",
                    "unit_amount": {"currency_code": "EUR", "value": "3.49"},
                    "quantity": "1",
                    "sku": "eo-fr",
                    "category": "DIGITAL_GOODS",
                }
            ],
            "payments": {
                "captures": [
                    {
                        "id": "capture-id",
                        "status": "COMPLETED",
                        "amount": {"currency_code": "EUR", "value": "3.49"},
                        "final_capture": True,
                        "seller_protection": {
                            "status": "ELIGIBLE",
                            "dispute_categories": ["ITEM_NOT_RECEIVED", "UNAUTHORIZED_TRANSACTION"],
                        },
                        "seller_receivable_breakdown": {
                            "gross_amount": {"currency_code": "EUR", "value": "3.49"},
                            "paypal_fee": {"currency_code": "EUR", "value": "0.45"},
                            "net_amount": {"currency_code": "EUR", "value": "3.04"},
                        },
                        "links": [
                            {
                                "href": "https://api.paypal.com/v2/payments/captures/capture-id",
                                "rel": "self",
                                "method": "GET",
                            },
                            {
                                "href": "https://api.paypal.com/v2/payments/captures/capture-id/refund",
                                "rel": "refund",
                                "method": "POST",
                            },
                            {
                                "href": f"https://api.paypal.com/v2/checkout/orders/{PURCHASE_ID}",
                                "rel": "up",
                                "method": "GET",
                            },
                        ],
                        "create_time": "2025-05-21T12:38:30Z",
                        "update_time": "2025-05-21T12:38:30Z",
                    }
                ]
            },
        }
    ],
    "payer": {
        "name": {"given_name": "Alice", "surname": "Dupont"},
        "email_address": "alice@example.org",
        "payer_id": "account-id",
    },
    "create_time": "2025-05-21T12:38:02Z",
    "update_time": STATUS_UPDATE_TIME,
    "links": [{"href": f"https://api.paypal.com/v2/checkout/orders/{PURCHASE_ID}", "rel": "self", "method": "GET"}],
}

PLAN_ID = "P-8TK09370UE116905RM7X56CQ"
SUBSCRIPTION_ID = "I-YSW93404E5CF"
SUBSCRIPTION_DATA = {
    "status": "ACTIVE",
    "status_update_time": STATUS_UPDATE_TIME,
    "id": SUBSCRIPTION_ID,
    "plan_id": PLAN_ID,
    "start_time": "2025-04-05T20:34:29Z",
    "quantity": "1",
    "shipping_amount": {"currency_code": "EUR", "value": "0.0"},
    "subscriber": {
        "email_address": "alice@example.org",
        "payer_id": "id",
        "name": {"given_name": "Alice", "surname": "Boba"},
        "tenant": "PAYPAL",
    },
    "billing_info": {
        "outstanding_balance": {"currency_code": "EUR", "value": "0.0"},
        "cycle_executions": [
            {
                "tenure_type": "REGULAR",
                "sequence": 1,
                "cycles_completed": 1,
                "cycles_remaining": 0,
                "current_pricing_scheme_version": 1,
                "total_cycles": 0,
            }
        ],
        "last_payment": {"amount": {"currency_code": "EUR", "value": "10.0"}, "time": "2025-04-05T20:34:41Z"},
        "next_billing_time": "2025-05-05T10:00:00Z",
        "failed_payments_count": 0,
    },
    "create_time": "2025-04-05T20:34:40Z",
    "update_time": "2025-04-05T20:34:42Z",
    "plan_overridden": False,
}

STRIPE_CHECKOUT_SESSION_ID = "cs_zzz"
STRIPE_PURCHASE_ID = "pi_nnn"
STRIPE_CHECKOUT_SESSION_CREATE_DATA = {
    "id": "cs_test_xxx",
    "object": "checkout.session",
    "adaptive_pricing": {"enabled": True},
    "after_expiration": None,
    "allow_promotion_codes": None,
    "amount_subtotal": 999,
    "amount_total": 999,
    "automatic_tax": {"enabled": False, "liability": None, "provider": None, "status": None},
    "billing_address_collection": None,
    "cancel_url": "https://.../#fr-ca",
    "client_reference_id": "01K4D2WZR8G1TG36RNF3020124-eo-fr",
    "client_secret": None,
    "collected_information": None,
    "consent": None,
    "consent_collection": None,
    "created": 1757844788,
    "currency": "eur",
    "currency_conversion": None,
    "custom_fields": [
        {
            "key": "dictionary",
            "label": {"custom": constants.PROJECT, "type": "custom"},
            "optional": False,
            "text": {"default_value": "eo-fr", "maximum_length": None, "minimum_length": None, "value": None},
            "type": "text",
        }
    ],
    "custom_text": {
        "after_submit": None,
        "shipping_address": None,
        "submit": None,
        "terms_of_service_acceptance": None,
    },
    "customer": None,
    "customer_creation": "if_required",
    "customer_details": None,
    "customer_email": None,
    "discounts": [],
    "expires_at": 1757931188,
    "invoice": None,
    "invoice_creation": {
        "enabled": False,
        "invoice_data": {
            "account_tax_ids": None,
            "custom_fields": None,
            "description": None,
            "footer": None,
            "issuer": None,
            "metadata": {},
            "rendering_options": None,
        },
    },
    "livemode": False,
    "locale": None,
    "metadata": {},
    "mode": "payment",
    "origin_context": None,
    "payment_intent": None,
    "payment_link": None,
    "payment_method_collection": "if_required",
    "payment_method_configuration_details": {"id": "pmc_1S3HZMDg4CrdeZvefiFqjEev", "parent": None},
    "payment_method_options": {
        "card": {"request_three_d_secure": "automatic"},
        "wechat_pay": {"app_id": None, "client": "web"},
    },
    "payment_method_types": [
        "card",
        "bancontact",
        "eps",
        "ideal",
        "p24",
        "alipay",
        "klarna",
        "multibanco",
        "wechat_pay",
        "link",
        "mobilepay",
        "paypal",
        "revolut_pay",
        "amazon_pay",
        "billie",
        "satispay",
    ],
    "payment_status": "unpaid",
    "permissions": None,
    "phone_number_collection": {"enabled": False},
    "recovered_from": None,
    "saved_payment_method_options": None,
    "setup_intent": None,
    "shipping_address_collection": None,
    "shipping_cost": None,
    "shipping_options": [],
    "status": "open",
    "submit_type": None,
    "subscription": None,
    "success_url": "https://.../enjoy",
    "total_details": {"amount_discount": 0, "amount_shipping": 0, "amount_tax": 0},
    "ui_mode": "hosted",
    "url": "https://checkout.stripe.com/c/pay/cs_test_xxx",
    "wallet_options": None,
}
STRIPE_CHECKOUT_SESSION_DATA = {
    "id": STRIPE_CHECKOUT_SESSION_ID,
    "client_reference_id": "01K4D2WZR8G1TG36RNF3020124-eo-fr",
    "created": 1757080888,
    "customer": None,
    "customer_details": {
        "email": "alice@example.org",
        "name": "Alice Baz",
    },
    "customer_email": None,
    "mode": "payment",
    "payment_intent": STRIPE_PURCHASE_ID,
    "payment_status": "paid",
    "status": "complete",
}
STRIPE_REFUND_DATA = {
    "id": STRIPE_CHECKOUT_SESSION_ID,
    "captured": True,
    "created": 1757080903,
    "paid": True,
    "payment_intent": STRIPE_PURCHASE_ID,
    "refunded": True,
}

ORDER_P = models.Order(
    PURCHASE_ID,
    dictionary="eo-fr",
    email="alice@example.org",
    invoice_id="capture-id",
    status="completed",
    status_update_time=STATUS_UPDATE_TIME,
    ulid="01JVRQ7C9RTEHHFPY30RDQYZPR",
    user="Alice",
)
ORDER_S = models.Order(
    SUBSCRIPTION_ID,
    email="alice@example.org",
    plan_id=PLAN_ID,
    status="active",
    status_update_time=STATUS_UPDATE_TIME,
    ulid="01JVRQ7C9RTEHHFPY30RDQYZPR",
    user="Alice",
)

PAYPAL_WEBHOOK_ID = "40L71081MK3756722"
PAYPAL_WEBHOOK_HEADERS = {
    "Paypal-Transmission-Time": "2025-04-05T20:32:44Z",
    "Paypal-Cert-Url": PAYPAL_CERT_URL,
    "Paypal-Transmission-Sig": "Dss1lP9Y8D+ZXQ5VIbW/91wykhEpH06KUSEOmIGceJlSd33AE1nBT/UiNxz/i4/6EP31a7Sx44CjLOQtkJ+LYWK5aA4YkVu/e+CZ/nMLB1FW6lJXEflt0DGRusNaBDpq7WrfCHNiScquRMh3E4eUODfTSowvsiPf2UWkfbk0e/ELMky8YaFTS6gIhUdaRh1U8lUbv+IXi7v5pSGQOTtmrHR28fvPc+D8fSsl0tBfakpRPUNskNmRwJYYngQ0NzAO7cNAzCf3Es5yEAiJW9FgjawHmOkeoWSjWIXH7SKO7q1tqCRCE/+iu3jtK3q+wmq6iVq1luglzndgqNKTw+DwaQ==",
    "Paypal-Transmission-Id": "212a639d-125d-11f0-8798-c5d6de2737a0",
}
PAYPAL_WEBHOOK_PAYLOAD = json.dumps(
    {
        "id": "WH-1F78928319310462G-18R51787X87914712",
        "event_version": "1.0",
        "create_time": "2025-04-05T20:32:40.508Z",
        "resource_type": "sale",
        "event_type": "PAYMENT.SALE.PENDING",
        "summary": "Payment pending for € 10.0 EUR",
        "resource": {
            "id": "10H81276XF6353701",
            "state": "completed",
            "amount": {"total": "10.00", "currency": "EUR", "details": {"subtotal": "10.00"}},
            "payment_mode": "INSTANT_TRANSFER",
            "protection_eligibility": "ELIGIBLE",
            "protection_eligibility_type": "ITEM_NOT_RECEIVED_ELIGIBLE,UNAUTHORIZED_PAYMENT_ELIGIBLE",
            "payment_hold_status": "HELD",
            "payment_hold_reasons": ["PAYMENT_HOLD"],
            "transaction_fee": {"value": "0.64", "currency": "EUR"},
            "invoice_number": "",
            "billing_agreement_id": "I-YSW93404E5CF",
            "create_time": "2025-04-05T20:32:35Z",
            "update_time": "2025-04-05T20:32:35Z",
            "links": [
                {
                    "href": "https://api.paypal.com/v1/payments/sale/10H81276XF6353701",
                    "rel": "self",
                    "method": "GET",
                },
                {
                    "href": "https://api.paypal.com/v1/payments/sale/10H81276XF6353701/refund",
                    "rel": "refund",
                    "method": "POST",
                },
            ],
            "soft_descriptor": "PAYPAL *READERDICT",
        },
        "links": [
            {
                "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-1F78928319310462G-18R51787X87914712",
                "rel": "self",
                "method": "GET",
            },
            {
                "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-1F78928319310462G-18R51787X87914712/resend",
                "rel": "resend",
                "method": "POST",
            },
        ],
    },
    separators=(",", ":"),
    ensure_ascii=False,
).encode()

STRIPE_WEBHOOK_HEADERS = {
    "Stripe-Signature": (
        "t=1757077813,"
        "v1=694c3add1ff8bcb080fc22aeda24d69d67fc9b08152e6d7b59aee98e9d7127fc,"
        "v0=5b153d30ed3e0d0b718d21d8057fc8ac3e89fa058c616aecb5be378c09666fc2"
    ),
}
STRIPE_WEBHOOK_PAYLOAD = json.dumps(
    {
        "id": "evt_3S3zLiDg4CrdeZve3jkGWhc6",
        "object": "event",
        "api_version": "2025-08-27.basil",
        "created": 1757077813,
        "data": {
            "object": {
                "id": "re_3S3zLiDg4CrdeZve3j41Xt9K",
                "object": "refund",
                "amount": 1449,
                "balance_transaction": "txn_3S3zLiDg4CrdeZve3wRejIFU",
                "charge": "ch_3S3zLiDg4CrdeZve3ciCk8Cu",
                "created": 1757077811,
                "currency": "eur",
                "destination_details": {
                    "card": {
                        "reference": "7693739506885588",
                        "reference_status": "available",
                        "reference_type": "acquirer_reference_number",
                        "type": "refund",
                    },
                    "type": "card",
                },
                "metadata": {},
                "payment_intent": "pi_3S3zLiDg4CrdeZve38cUeM4j",
                "reason": "requested_by_customer",
                "receipt_number": None,
                "source_transfer_reversal": None,
                "status": "succeeded",
                "transfer_reversal": None,
            },
            "previous_attributes": {
                "destination_details": {"card": {"reference_status": "pending", "reference": None}}
            },
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {"id": None, "idempotency_key": None},
        "type": "charge.refund.updated",
    },
    indent=2,
    ensure_ascii=False,
).encode()
