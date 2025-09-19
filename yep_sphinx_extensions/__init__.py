"""Sphinx extensions for performant YEP processing"""

from __future__ import annotations

import html
from pathlib import Path
from typing import TYPE_CHECKING, Any

from docutils.writers.html5_polyglot import HTMLTranslator
from sphinx import environment

from yep_sphinx_extensions.generate_rss import (
    create_rss_feed,
    get_from_doctree,
    yep_abstract,
)
from yep_sphinx_extensions.yep_processor.html import (
    yep_html_builder,
    yep_html_translator,
)
from yep_sphinx_extensions.yep_processor.parsing import (
    yep_banner_directive,
    yep_parser,
    yep_role,
)
from yep_sphinx_extensions.yep_processor.transforms import yep_references
from yep_sphinx_extensions.yep_zero_generator.yep_index_generator import create_yep_zero

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def _update_config_for_builder(app: Sphinx) -> None:
    app.env.document_ids = {}  # For YEPReferenceRoleTitleText
    app.env.settings["builder"] = app.builder.name
    if app.builder.name == "dirhtml":
        app.env.settings["yep_url"] = "yep-{:0>4}/"

    app.connect("build-finished", _post_build)  # Post-build tasks


def _post_build(app: Sphinx, exception: Exception | None) -> None:
    from pathlib import Path

    from build import create_index_file

    if exception is not None:
        return

    # internal_builder exists if Sphinx is run by build.py
    if "internal_builder" not in app.tags:
        create_index_file(Path(app.outdir), app.builder.name)
    create_rss_feed(app.doctreedir, app.outdir)


def set_description(
    app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree
) -> None:
    if not pagename.startswith("yep-"):
        return

    full_path = Path(app.doctreedir) / f"{pagename}.doctree"
    abstract = get_from_doctree(full_path, "Abstract")
    if abstract:
        if len(abstract) > 256:
            abstract = abstract[:253] + "..."
        context["description"] = html.escape(abstract)
    else:
        context["description"] = "Yocto Enhancement Proposals (YEPs)"


def setup(app: Sphinx) -> dict[str, bool]:
    """Initialize Sphinx extension."""

    environment.default_settings["yep_url"] = "yep-{:0>4}.html"
    environment.default_settings["halt_level"] = 2  # Fail on Docutils warning

    # Register plugin logic
    app.add_builder(yep_html_builder.FileBuilder, override=True)
    app.add_builder(yep_html_builder.DirectoryBuilder, override=True)

    app.add_source_parser(yep_parser.YEPParser)  # Add YEP transforms

    app.set_translator("html", yep_html_translator.YEPTranslator)  # Docutils Node Visitor overrides (html builder)
    app.set_translator("dirhtml", yep_html_translator.YEPTranslator)  # Docutils Node Visitor overrides (dirhtml builder)

    app.add_role("yep", yep_role.YEPRole(), override=True)  # Transform YEP references to links

    app.add_post_transform(yep_references.YEPReferenceRoleTitleText)

    # Register custom directives
    app.add_directive(
        "yep-banner", yep_banner_directive.YEPBanner)
    app.add_directive(
        "canonical-doc", yep_banner_directive.CanonicalDocBanner)
    app.add_directive(
        "canonical-pypa-spec", yep_banner_directive.CanonicalPyPASpecBanner)
    app.add_directive(
        "canonical-typing-spec", yep_banner_directive.CanonicalTypingSpecBanner)
    app.add_directive("rejected", yep_banner_directive.RejectedBanner)
    app.add_directive("superseded", yep_banner_directive.SupersededBanner)
    app.add_directive("withdrawn", yep_banner_directive.WithdrawnBanner)

    # Register event callbacks
    app.connect("builder-inited", _update_config_for_builder)  # Update configuration values for builder used
    app.connect("env-before-read-docs", create_yep_zero)  # YEP 0 hook
    app.connect('html-page-context', set_description)

    # Mathematics rendering
    inline_maths = HTMLTranslator.visit_math, None
    block_maths = HTMLTranslator.visit_math_block, None
    app.add_html_math_renderer("maths_to_html", inline_maths, block_maths)  # Render maths to HTML

    # Parallel safety: https://www.sphinx-doc.org/en/master/extdev/index.html#extension-metadata
    return {"parallel_read_safe": True, "parallel_write_safe": True}
