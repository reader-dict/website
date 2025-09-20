from functools import cache
from subprocess import check_output

from src import constants, utils

TEMPLATES = {"": "home", "get": "landing", "sponsors": "sponsor"}
# `-1` restricts to the very last time the file changed
# `%cs` is the committer date, short format (YYYY-MM-DD)
LAST_MOD_TIME_CMD = ["git", "log", "-1", "--pretty=%cs"]


@cache
def last_modified(template: str) -> str:
    template = TEMPLATES.get(template, template)
    command = [*LAST_MOD_TIME_CMD, str(constants.VIEW / f"{template}.tpl")]
    return check_output(command, text=True).strip()  # noqa: S603


def generate_sitemap() -> None:
    dictionaries = utils.load_dictionaries(keys=constants.DICTIONARY_KEYS_MINIMAL)
    monolingual = sorted({key for key in dictionaries if key in dictionaries[key]})
    links: list[str] = [
        *[f"download/{lang}" for lang in monolingual],
        "",
        "hall-of-fame",
        "legal-mentions",
        "list",
        "sponsors",
    ]
    for lang_src, langs_dst in dictionaries.items():
        links.extend(f"get/{lang_src}/{lang_dst}" for lang_dst in langs_dst if lang_src != lang_dst)

    fmt = f"<url><loc>https://www.{constants.WWW}/{{}}</loc><lastmod>{{}}</lastmod></url>"
    content = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *[fmt.format(link, last_modified(link.split("/", 1)[0])) for link in sorted(links)],
            "</urlset>",
            "",
        ]
    )
    file = constants.ASSET / "sitemap.xml"
    if file.read_text() != content:
        file.write_text(content)


if __name__ == "__main__":
    generate_sitemap()
