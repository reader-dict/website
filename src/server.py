import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import bottle
import bottle_file_cache
import secure
import ulid

from src import __version__, cache, constants, metrics, paypal, utils

log = logging.getLogger(__name__)
app = bottle.default_app()
CSP_NONCE = str(ulid.ULID())

# Inspired from `secure.Preset.STRICT` + tweaks for PayPal integration
secure_headers = secure.Secure(
    coep=secure.CrossOriginEmbedderPolicy().unsafe_none(),
    coop=secure.CrossOriginOpenerPolicy().same_origin_allow_popups(),
    # csp=secure.ContentSecurityPolicy()  # noqa: ERA001
    # .base_uri("'none'")
    # .default_src("'self'")
    # .frame_ancestors("'none'")
    # .frame_src("none' https://www.paypal.com")
    # .img_src("'self' https://www.paypalobjects.com")
    # .object_src("'none'")
    # .script_src("'self' https://www.paypal.com https://browser.sentry-cdn.com")
    # .style_src("'self'"),
    hsts=secure.StrictTransportSecurity().max_age(63072000).include_subdomains().preload(),
    permissions=secure.PermissionsPolicy().geolocation().microphone().camera(),
    referrer=secure.ReferrerPolicy().strict_origin_when_cross_origin(),
    server=secure.Server().set(""),
    xcto=secure.XContentTypeOptions().nosniff(),
    xfo=secure.XFrameOptions().deny(),
)


YEAR = datetime.now(tz=UTC).year
SUPPORTED_LOCALES = ["ca", "da", "de", "el", "en", "eo", "es", "fr", "it", "no", "pt", "ro", "ru", "sv"]
LOCALES = rf"({'|'.join(SUPPORTED_LOCALES)})"


def client_ip() -> str:
    return bottle.request.remote_addr or "unknown"


def render(tpl: str, **kwargs: Any) -> str:  # noqa: ANN401
    """Call the renderer with several common variables."""
    variables = {
        "constants": constants,
        "debug": bottle.DEBUG,
        "description": utils.tr("header-slogan"),
        "page": tpl,
        "request": bottle.request,
        "sentry_environment": constants.SENTRY_ENV_DEV if bottle.DEBUG else constants.SENTRY_ENV_PROD,
        "sentry_release": __version__,
        "tr": utils.tr,
        "url": bottle.request.url,
        "url_pure": bottle.request.url.split("?", 1)[0],
        "version": uuid.uuid4() if bottle.DEBUG else __version__,
        "year": YEAR,
    } | kwargs
    return bottle.jinja2_template(tpl, template_lookup=[constants.VIEW], **variables)


@app.hook("after_request")
def add_security_headers() -> None:
    """Apply strict security headers."""
    secure_headers.set_headers(bottle.response)


@app.error(400)
@app.error(403)
@app.error(404)
@app.error(410)
def custom_error(error: bottle.HTTPError) -> str:
    return render("error", error=error.status_code, title="🤦")


@app.get(constants.ROUTE_API_DICT)
@bottle_file_cache.cache()
def api_dictionary_get() -> str:
    bottle.response.content_type = "application/json"
    return json.dumps(utils.load_dictionaries(), check_circular=False, separators=(",", ":"))


@app.post(constants.ROUTE_API_ORDER)
def api_order() -> str:
    event = bottle.request.json
    kind = "purchase" if "payer" in event else "subscription"
    log.info("PayPal %s received from IP %r: %r", kind, client_ip(), event)
    order_id = event.get("subscriptionID") or event["id"]

    bottle.response.content_type = "application/json"
    return paypal.register_order(kind, order_id)


@app.post(constants.ROUTE_API_WEBHOOK_PAYPAL)
def api_webhook_paypal() -> bottle.HTTPResponse:
    headers = dict(bottle.request.headers)
    payload = bottle.request.body.read()
    log.info("PayPal webhook received, headers = %s, payload = %r", headers, payload)

    if paypal.is_valid_webhook_event(headers, payload):
        resp = paypal.handle_webhook(json.loads(payload))
        log.info("PayPal webhook order handled: %s", resp)
    else:
        log.error("PayPal webhook signature failed")

    return bottle.response


@app.get("/asset/<kind>/<file>")
def asset(kind: str, file: str) -> bottle.HTTPResponse:
    response = bottle.static_file(file, root=constants.ASSET / kind)
    response.set_header("Cache-Control", "public, max-age=31536000, immutable")
    return response


@app.get("/file/<lang>/<file_name>")
def download_monolingual(lang: str, file_name: str) -> bottle.HTTPResponse:
    try:
        fmt = utils.get_format_from_file_name(lang, file_name)
    except FileNotFoundError:
        raise bottle.HTTPError(status=404) from None

    if not (constants.FILES / lang / lang / file_name).is_file():
        raise bottle.HTTPError(status=404) from None

    etym = "noetym" if "noetym" in file_name else "full"
    metrics.plus_one(f"{lang}-{lang}", fmt, etym)
    return bottle.static_file(file_name, root=constants.FILES / lang / lang, download=True)


@app.get("/file/<uid>")
def download_bilingual(uid: str) -> bottle.HTTPResponse:
    try:
        order_type, order_id, lang_src, lang_dst, file_name, fmt = cache.get(uid)
    except cache.CacheError:
        log.warning("File cache expired, or inexistant: %s", uid)
        raise bottle.HTTPError(status=410) from None

    folder = constants.PURCHASE_FILES / order_id if order_type == "purchase" else constants.FILES / lang_src / lang_dst

    if not (folder / file_name).is_file():
        log.critical("A file is missing in the %s-%s dictionary: %s", lang_src, lang_dst, file_name)
        raise bottle.HTTPError(status=404) from None

    log.info("[/file %s ID=%r] Downloaded %s from IP %r", order_type, order_id, file_name, client_ip())

    etym = "noetym" if "noetym" in file_name else "full"
    metrics.plus_one(f"{lang_src}-{lang_dst}", fmt, etym)

    headers = {"File-Source": order_type}
    return bottle.static_file(file_name, root=folder, download=True, headers=headers)


@app.get("/download/<lang>")
@bottle_file_cache.cache()
def downloads_monolingual(lang: str) -> str:
    try:
        dictionary = utils.load_dictionaries()[lang][lang]
    except KeyError:
        log.error(  # noqa: TRY400
            "[/download monolingual] The dictionary %s-%s does not exist, or is disabled", lang, lang
        )
        raise bottle.HTTPError(status=404) from None

    links = utils.craft_downloads_url(dictionary)
    description = utils.tr("download-page-title-monolingual", utils.tr(lang))
    description_full = utils.tr("download-page-description-monolingual", utils.tr(lang))
    return render(
        "download",
        dictionary=dictionary,
        description=description,
        description_full=description_full,
        kind="monolingual",
        links=links,
        name=utils.tr("hello"),
        title=description,
    )


@app.get(f"/<locale:re:{LOCALES}>/download/<lang_src>/<lang_dst>/<subscription_id>")
def downloads_bilingual_old(locale: str, lang_src: str, lang_dst: str, subscription_id: str) -> str:  # noqa: ARG001
    """Old URL, shared to customers before 2025-05-16."""
    bottle.request.params["order"] = subscription_id
    return downloads_bilingual(lang_src, lang_dst)


@app.get("/download/<lang_src>/<lang_dst>")
@bottle_file_cache.cache(params=["order", "checkpoint", "subscription"])
def downloads_bilingual(lang_src: str, lang_dst: str) -> str:
    params = bottle.request.params

    if not (order_id := params.get("order", "") or params.get("subscription", "")) or not utils.is_checkpoint(
        checkpoint := params.get("checkpoint", "")
    ):
        log.error("[/download bilingual] Missing mandatory details")
        raise bottle.HTTPError(status=400) from None

    if not (order := utils.get_order(order_id)):
        log.error("[/download order ID=%r] No order with that ID", order_id)
        raise bottle.HTTPError(status=404) from None

    if not (dictionary := utils.get_dictionary_metadata(order, lang_src, lang_dst)):
        log.error(
            "[/download order ID=%r] The dictionary %s-%s does not exist, or is disabled",
            order.id,
            lang_src,
            lang_dst,
        )
        raise bottle.HTTPError(status=404) from None

    dict_available = order.target_dictionary
    dict_requested = dictionary["name"]
    if dict_available != dict_requested:
        log.error(
            "[/download order ID=%r] Dictionary mismatch: requested=%r, available=%r",
            order.id,
            dict_requested,
            dict_available,
        )
        raise bottle.HTTPError(status=403) from None

    verified_checkpoint = order.checkpoint
    if verified_checkpoint != checkpoint:
        log.error("[/download order ID=%r] Checkpoint %r is invalid", order.id, checkpoint)
        raise bottle.HTTPError(status=403) from None

    log.info("[/download] Order %s", order.as_dict())
    if not order.status_ok:
        log.info("[/download order ID=%r] Status does not allow to continue", order.id)
        raise bottle.HTTPError(status=403) from None

    links = utils.craft_downloads_url(dictionary, order_type=order.type, order_id=order.id)
    kind = "universal" if lang_src == "all" else "bilingual"
    localized_dst = utils.tr(lang_dst)
    localized_src = utils.tr(lang_src)
    description = utils.tr(f"download-page-title-{kind}", localized_src, localized_dst)
    description_full = utils.tr(f"download-page-description-{kind}", localized_src, localized_dst)
    return render(
        "download",
        description=description,
        description_full=description_full,
        dictionary=dictionary,
        kind="bilingual",
        links=links,
        name=bottle.html_escape(order.user),
        order=order,
        title=description,
    )


@app.get("/hall-of-fame")
def hall_of_fame() -> str:
    return render("hall-of-fame", title="🏆")


@app.get("/")
@bottle_file_cache.cache()
def home() -> str:
    return render("home", dictionaries=utils.load_dictionaries(), title="📚")


@app.get("/ads.txt")
def ads() -> bottle.HTTPResponse:
    return bottle.static_file("ads.txt", root=constants.ASSET)


@app.get("/humans.txt")
def humans() -> bottle.HTTPResponse:
    return bottle.static_file("humans.txt", root=constants.ASSET)


@app.get("/robots.txt")
def robots() -> bottle.HTTPResponse:
    return bottle.static_file("robots.txt", root=constants.ASSET)


@app.get("/.well-known/security.txt")
def security() -> bottle.HTTPResponse:
    return bottle.static_file("security.txt", root=constants.ASSET)


@app.get("/sitemap.xml")
def sitemap() -> bottle.HTTPResponse:
    return bottle.static_file("sitemap.xml", root=constants.ASSET)


def main() -> None:  # pragma: nocover
    """Entry point."""
    logging.basicConfig(
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    bottle.run(server=constants.SERVER, host=constants.HOST, port=constants.PORT, debug=True, reloader=True)


#
# Old URL (before 2025-07-xx)
#


@app.get(f"/<locale:re:{LOCALES}>/file/<lang>/<file_name>")
def download_monolingual_localized(locale: str, lang: str, file_name: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect(f"/file/{lang}/{file_name}")


@app.get(f"/<locale:re:{LOCALES}>/file/<uid>")
def download_bilingual_localized(locale: str, uid: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect(f">/file/{uid}")


@app.get(f"/<locale:re:{LOCALES}>/download/<lang>")
def downloads_monolingual_localized(locale: str, lang: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect(f"/download/{lang}")


@app.get(f"/<locale:re:{LOCALES}>/download/<lang_src>/<lang_dst>")
def downloads_bilingual_localized(_: str, lang_src: str, lang_dst: str) -> None:  # pragma: nocover
    bottle.redirect(f"/download/{lang_src}/{lang_dst}")  # pragma: nocover


@app.get(f"/<locale:re:{LOCALES}>/faq")
def faq_localized(locale: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect("/")


@app.get(f"/<locale:re:{LOCALES}>")
@app.get(f"/<locale:re:{LOCALES}>/")
def home_localized(locale: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect("/")
