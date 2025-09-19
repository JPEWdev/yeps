from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx import parsers

from yep_sphinx_extensions.yep_processor.transforms import yep_contents
from yep_sphinx_extensions.yep_processor.transforms import yep_footer
from yep_sphinx_extensions.yep_processor.transforms import yep_headers
from yep_sphinx_extensions.yep_processor.transforms import yep_title

if TYPE_CHECKING:
    from docutils import transforms


class YEPParser(parsers.RSTParser):
    """RST parser with custom YEP transforms."""

    supported = ("yep", "yocto-enhancement-proposal")  # for source_suffix in conf.py

    def __init__(self):
        """Mark the document as containing RFC 2822 headers."""
        super().__init__(rfc2822=True)

    def get_transforms(self) -> list[type[transforms.Transform]]:
        """Use our custom YEP transform rules."""
        return [
            yep_headers.YEPHeaders,
            yep_title.YEPTitle,
            yep_contents.YEPContents,
            yep_footer.YEPFooter,
        ]
