from datetime import UTC, datetime

from src import constants, utils


def generate_sitemap() -> None:
    dictionaries = utils.load_dictionaries()
    langs = sorted({key for key in dictionaries if key in dictionaries[key]})
    last_mod = f"</loc><lastmod>{datetime.now(tz=UTC).isoformat()[:10]}</lastmod></url>"
    links: list[str] = [f"download/{lang}" for lang in langs]

    content = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            f"<url><loc>https://www.{constants.WWW}/hall-of-fame{last_mod}",
            *[f"<url><loc>https://www.{constants.WWW}/{link}{last_mod}" for link in sorted(links)],
            "</urlset>",
            "",
        ]
    )
    file = constants.ASSET / "sitemap.xml"
    if file.read_text() != content:
        file.write_text(content)


if __name__ == "__main__":
    generate_sitemap()
