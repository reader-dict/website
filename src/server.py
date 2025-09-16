import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import bottle
import bottle_file_cache
import minify_html
import rcssmin
import rjsmin
import secure
import ulid

from src import __version__, cache, constants, handlers, metrics, utils

log = logging.getLogger(__name__)
app = bottle.default_app()
CSP_NONCE = str(ulid.ULID())

# Inspired from `secure.Preset.STRICT` + tweaks for inline font
secure_headers = secure.Secure(
    coep=secure.CrossOriginEmbedderPolicy().unsafe_none(),
    coop=secure.CrossOriginOpenerPolicy().same_origin_allow_popups(),
    csp=secure.ContentSecurityPolicy().style_src("'self'"),
    hsts=secure.StrictTransportSecurity().max_age(63072000).include_subdomains().preload(),
    permissions=secure.PermissionsPolicy().geolocation().microphone().camera(),
    referrer=secure.ReferrerPolicy().strict_origin_when_cross_origin(),
    server=secure.Server().set(""),
    xcto=secure.XContentTypeOptions().nosniff(),
    xfo=secure.XFrameOptions().deny(),
)


YEAR = datetime.now(tz=UTC).year
SUPPORTED_LOCALES = ["ca", "da", "de", "el", "en", "eo", "es", "fr", "it", "no", "pt", "ro", "ru", "sv", "zh"]
LOCALES = rf"({'|'.join(SUPPORTED_LOCALES)})"


def client_ip() -> str:
    return bottle.request.remote_addr or "unknown"


def render(tpl: str, **kwargs: Any) -> str:  # noqa: ANN401
    """Call the renderer with several common variables."""
    variables = {
        "constants": constants,
        "debug": bottle.DEBUG,
        "title": constants.HEADER_SLOGAN,
        "language": utils.language,
        "url_pure": bottle.request.url.split("?", 1)[0],
        "version": uuid.uuid4() if bottle.DEBUG else __version__,
        "year": YEAR,
    } | kwargs
    return minify_html.minify(bottle.jinja2_template(tpl, template_lookup=[constants.VIEW], **variables))


@app.hook("after_request")
def add_security_headers() -> None:
    """Apply strict security headers."""
    secure_headers.set_headers(bottle.response)


@app.error(400)
@app.error(403)
@app.error(404)
@app.error(410)
def custom_error(error: bottle.HTTPError) -> str:
    match error.status_code:
        case 400:
            msg = "This link is malformed."
        case 403:
            msg = "This link does not grant access to that dictionary."
        case 410:
            msg = "The link to the file you requested has either expired, or never existed."
        case _:  # 404, and others
            msg = "The page you are looking for does not exist."
    return render("error", title="Error", msg=msg)


@app.get(constants.ROUTE_API_DICT)
@bottle_file_cache.cache()
def api_dictionary_get() -> str:
    bottle.response.content_type = "application/json"
    return json.dumps(
        utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_MINIMAL),
        check_circular=False,
        separators=(",", ":"),
    )


@app.get(f"{constants.ROUTE_API_PRE_ORDER}/<lang_src>/<lang_dst>")
def api_pre_order(lang_src: str, lang_dst: str) -> dict[str, str]:
    bottle.response.content_type = "application/json"
    stripe = handlers.get("stripe")
    ret = stripe.create_checkout_session_url(lang_src, lang_dst)  # type: ignore[attr-defined]
    log.info("[/pre-order] Client reference ID %r from IP %r", ret["client_reference_id"], client_ip())
    return {"url": ret["url"]}


@app.post(constants.ROUTE_API_WEBHOOK)
def api_webhook(source: str) -> str:
    headers = dict(bottle.request.headers)
    payload = bottle.request.body.read()
    log.info("[%s] webhook received, headers = %s, payload = %r", source, headers, payload)

    if source not in handlers.SUPPORTED_HANDLERS:  # pragma: nocover
        log.error("Unknown webhook source: %r", source)
        raise bottle.HTTPError(status=404) from None

    bottle.response.content_type = "application/json"
    handler = handlers.get(source)
    if handler.is_valid_webhook_event(headers, payload):
        resp = handler.handle_webhook(json.loads(payload))
        log.info("[%s] Webhook order handled, status: %s", source, resp["status"])
        return json.dumps(resp)

    log.error("[%s] Webhook signature failed", source)
    return '{"error": "webhook signature failed"}'


@app.get(r"/asset/style/<file:re:\w+\.css>")
# @bottle_file_cache.cache(params=["v"])
def asset_css(file: str) -> bottle.HTTPResponse:
    try:
        content = (constants.ASSET / "style" / file).read_text(encoding=constants.ENCODING)
    except FileNotFoundError:
        raise bottle.HTTPError(status=404) from None

    cache_file = constants.FILES_CACHE / f"{file}.min.css"
    cache_file.write_text(rcssmin.cssmin(content), encoding=constants.ENCODING)

    response = bottle.static_file(cache_file.name, root=constants.FILES_CACHE)
    response.set_header("Cache-Control", "public, max-age=31536000, immutable")
    return response


@app.get(r"/asset/script/<file:re:\w+\.js>")
# @bottle_file_cache.cache(params=["v"])
def asset_js(file: str) -> bottle.HTTPResponse:
    try:
        content = (constants.ASSET / "script" / file).read_text(encoding=constants.ENCODING)
    except FileNotFoundError:
        raise bottle.HTTPError(status=404) from None

    cache_file = constants.FILES_CACHE / f"{file}.min.js"
    cache_file.write_text(rjsmin.jsmin(content), encoding=constants.ENCODING)

    response = bottle.static_file(cache_file.name, root=constants.FILES_CACHE)
    response.set_header("Cache-Control", "public, max-age=31536000, immutable")
    return response


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

    folder = constants.FILES / lang_src / lang_dst

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
        dictionary = utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_DOWNLOAD)[lang][lang]
    except KeyError:
        log.error(  # noqa: TRY400
            "[/download monolingual] The dictionary %s-%s does not exist, or is disabled", lang, lang
        )
        raise bottle.HTTPError(status=404) from None

    links = utils.craft_downloads_url(dictionary)
    last_updated = utils.get_last_modification_time(dictionary)
    return render(
        "download",
        dictionary=dictionary,
        last_updated=last_updated,
        links=links,
        title=f"{utils.language(lang)} monolingual dictionary",
    )


@app.get("/download/<lang_src>/<lang_dst>")
@bottle_file_cache.cache(params=["order", "checkpoint", "subscription"])
def downloads_bilingual(lang_src: str, lang_dst: str) -> str:
    params = bottle.request.params
    ip_addr = client_ip()

    if not (order_id := params.get("order", "") or params.get("subscription", "")) or not utils.is_checkpoint(
        checkpoint := params.get("checkpoint", "")
    ):
        log.error("[/download bilingual] Missing mandatory details (from %s)", ip_addr)
        raise bottle.HTTPError(status=400) from None

    if not (order := utils.get_order(order_id)):
        log.error("[/download order ID=%r] No order with that ID", order_id)
        raise bottle.HTTPError(status=404) from None

    if not (dictionary := utils.get_dictionary_metadata(lang_src, lang_dst)):
        log.error(
            "[/download order ID=%r] The dictionary %s-%s does not exist, or is disabled (from %s)",
            order.id,
            lang_src,
            lang_dst,
            ip_addr,
        )
        raise bottle.HTTPError(status=404) from None

    dict_available = order.target_dictionary
    dict_requested = dictionary["name"]
    if dict_available != dict_requested:
        log.error(
            "[/download order ID=%r] Dictionary mismatch: requested=%r, available=%r (from %s)",
            order.id,
            dict_requested,
            dict_available,
            ip_addr,
        )
        raise bottle.HTTPError(status=403) from None

    verified_checkpoint = order.checkpoint
    if verified_checkpoint != checkpoint:
        log.error("[/download order ID=%r] Checkpoint %r is invalid (from %s)", order.id, checkpoint, ip_addr)
        raise bottle.HTTPError(status=403) from None

    log.info("[/download from IP=%r] Order %s", ip_addr, order.as_dict())
    if not order.status_ok:
        log.info("[/download order ID=%r] Status does not allow to continue (from %s)", order.id, ip_addr)
        raise bottle.HTTPError(status=403) from None

    links = utils.craft_downloads_url(dictionary, order_type=order.type, order_id=order.id)
    localized_dst = utils.language(lang_dst)
    localized_src = utils.language(lang_src)
    title = (
        f"{localized_src} {localized_dst} dictionary"
        if lang_src == "all"
        else f"{localized_src} - {localized_dst} bilingual dictionary"
    )
    last_updated = utils.get_last_modification_time(dictionary)
    return render("download", dictionary=dictionary, last_updated=last_updated, links=links, title=title)


@app.get("/get/<lang_src>/<lang_dst>")
@bottle_file_cache.cache()
def landing_page_bilingual(lang_src: str, lang_dst: str) -> str:
    try:
        dictionary = utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_DOWNLOAD)[lang_src][lang_dst]
    except KeyError:
        log.error(  # noqa: TRY400
            "[/get bilingual] The dictionary %s-%s does not exist, or is disabled", lang_src, lang_dst
        )
        raise bottle.HTTPError(status=404) from None

    localized_dst = utils.language(lang_dst)
    localized_src = utils.language(lang_src)
    title = (
        f"{localized_src} {localized_dst} dictionary"
        if lang_src == "all"
        else f"{localized_src} - {localized_dst} bilingual dictionary"
    )
    return render("landing", dictionary=dictionary, last_updated=dictionary["updated"], title=title)


@app.get("/enjoy")
@bottle_file_cache.cache()
def enjoy() -> str:
    return render("enjoy")


@app.get("/hall-of-fame")
@bottle_file_cache.cache()
def hall_of_fame() -> str:
    return render("hall-of-fame", title="Hall of Fame")


@app.get("/")
@bottle_file_cache.cache()
def home() -> str:
    return render(
        "home",
        dictionaries=utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_MINIMAL),
        reviews=utils.create_dictionary_links(utils.random_reviews(2)),
    )


@app.get("/list")
@bottle_file_cache.cache()
def list_all() -> str:
    return render(
        "list",
        dictionaries=utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_MINIMAL),
    )


@app.get("/sponsors")
@bottle_file_cache.cache()
def sponsors() -> str:
    return render("sponsor", sponsors=utils.load_sponsors())


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
# Old URL (before 2025-09-09)
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
def downloads_bilingual_localized(locale: str, lang_src: str, lang_dst: str) -> None:  # noqa: ARG001  # pragma: nocover
    params = "&".join(f"{k}={v}" for k, v in bottle.request.params.items())
    bottle.redirect(f"/download/{lang_src}/{lang_dst}?{params}")  # pragma: nocover


@app.get(f"/<locale:re:{LOCALES}>/faq")
def faq_localized(locale: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect("/")


@app.get(f"/<locale:re:{LOCALES}>")
@app.get(f"/<locale:re:{LOCALES}>/")
def home_localized(locale: str) -> None:  # noqa: ARG001  # pragma: nocover
    bottle.redirect("/")


#
# Old URL (before 2025-05-16)
#


@app.get(f"/<locale:re:{LOCALES}>/download/<lang_src>/<lang_dst>/<order_id>")
def downloads_bilingual_old(locale: str, lang_src: str, lang_dst: str, order_id: str) -> None:  # noqa: ARG001
    """Old URL, shared to customers before 2025-05-16."""
    bottle.request.params["order"] = order_id
    params = "&".join(f"{k}={v}" for k, v in bottle.request.params.items())
    bottle.redirect(f"/download/{lang_src}/{lang_dst}?{params}")  # pragma: nocover
