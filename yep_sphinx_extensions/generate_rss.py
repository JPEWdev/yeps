# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

from __future__ import annotations

import datetime as dt
import pickle
from email.utils import format_datetime, getaddresses
from html import escape
from pathlib import Path

from docutils import nodes

RSS_DESCRIPTION = (
    "Newest Yocto Enhancement Proposals (YEPs): "
    "Information on new language features "
    "and some meta-information like release procedure and schedules."
)


def _format_rfc_2822(datetime: dt.datetime) -> str:
    datetime = datetime.replace(tzinfo=dt.timezone.utc)
    return format_datetime(datetime, usegmt=True)


document_cache: dict[Path, dict[str, str]] = {}


def get_from_doctree(full_path: Path, text: str) -> str:
    # Try and retrieve from cache
    if full_path in document_cache:
        return document_cache[full_path].get(text, "")

    # Else load doctree
    document = pickle.loads(full_path.read_bytes())
    # Store the headers (populated in the YEPHeaders transform)
    document_cache[full_path] = path_cache = document.get("headers", {})
    # Store the Abstract
    path_cache["Abstract"] = yep_abstract(document)
    # Return the requested key
    return path_cache.get(text, "")


def yep_creation(full_path: Path) -> dt.datetime:
    created_str = get_from_doctree(full_path, "Created")
    try:
        return dt.datetime.strptime(created_str, "%d-%b-%Y")
    except ValueError:
        return dt.datetime.min


def yep_abstract(document: nodes.document) -> str:
    """Return the first paragraph of the YEP abstract.
    If not found, return the first paragraph of the introduction.
    """
    introduction = ""
    for node in document.findall(nodes.section):
        title_node = node.next_node(nodes.title)
        if title_node is None:
            continue

        if title_node.astext() == "Abstract":
            if (para_node := node.next_node(nodes.paragraph)) is not None:
                return para_node.astext().strip().replace("\n", " ")
            return ""
        if title_node.astext() == "Introduction":
            introduction = node.next_node(nodes.paragraph).astext().strip().replace("\n", " ")

    return introduction


def _generate_items(doctree_dir: Path):
    # get list of yeps with creation time (from "Created:" string in yep source)
    yeps_with_dt = sorted((yep_creation(path), path) for path in doctree_dir.glob("yep-????.doctree"))

    # generate rss items for 10 most recent yeps (in reverse order)
    for datetime, full_path in reversed(yeps_with_dt[-10:]):
        try:
            yep_num = int(get_from_doctree(full_path, "YEP"))
        except ValueError:
            continue

        title = get_from_doctree(full_path, "Title")
        url = f"https://JPEWdev.github.io/yeps/yep-{yep_num:0>4}/"
        abstract = get_from_doctree(full_path, "Abstract")
        author = get_from_doctree(full_path, "Author")
        if "@" in author or " at " in author:
            parsed_authors = getaddresses([author])
            joined_authors = ", ".join(f"{name} ({email_address})" for name, email_address in parsed_authors)
        else:
            joined_authors = author

        item = f"""\
    <item>
      <title>YEP {yep_num}: {escape(title, quote=False)}</title>
      <link>{escape(url, quote=False)}</link>
      <description>{escape(abstract, quote=False)}</description>
      <author>{escape(joined_authors, quote=False)}</author>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{_format_rfc_2822(datetime)}</pubDate>
    </item>"""
        yield item


def create_rss_feed(doctree_dir: Path, output_dir: Path):
    # The rss envelope
    last_build_date = _format_rfc_2822(dt.datetime.now(dt.timezone.utc))
    items = "\n".join(_generate_items(Path(doctree_dir)))
    output = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">
  <channel>
    <title>Newest Yocto YEPs</title>
    <link>https://JPEWdev.github.io/yeps/</link>
    <description>{RSS_DESCRIPTION}</description>
    <atom:link href="https://JPEWdev.github.io/yeps/yeps.rss" rel="self"/>
    <docs>https://cyber.harvard.edu/rss/rss.html</docs>
    <language>en</language>
    <lastBuildDate>{last_build_date}</lastBuildDate>
{items}
  </channel>
</rss>
"""

    # output directory for target HTML files
    Path(output_dir, "yeps.rss").write_text(output, encoding="utf-8")
