"""Code for handling object representation of a YEP."""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Sequence
from email.parser import HeaderParser
from pathlib import Path

from yep_sphinx_extensions.yep_zero_generator.constants import ACTIVE_ALLOWED
from yep_sphinx_extensions.yep_zero_generator.constants import HIDE_STATUS
from yep_sphinx_extensions.yep_zero_generator.constants import SPECIAL_STATUSES
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_ACTIVE
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_PROVISIONAL
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_VALUES
from yep_sphinx_extensions.yep_zero_generator.constants import TYPE_STANDARDS
from yep_sphinx_extensions.yep_zero_generator.constants import TYPE_VALUES
from yep_sphinx_extensions.yep_zero_generator.errors import YEPError


@dataclasses.dataclass(order=True, frozen=True)
class _Author:
    """Represent YEP authors."""
    full_name: str  # The author's name.
    email: str  # The author's email address.


class YEP:
    """Representation of YEPs.

    Attributes:
        number : YEP number.
        title : YEP title.
        yep_type : The type of YEP.  Can only be one of the values from TYPE_VALUES.
        status : The YEP's status.  Value must be found in STATUS_VALUES.
        authors : A list of the authors.

    """

    # The required RFC 822 headers for all YEPs.
    required_headers = {"YEP", "Title", "Author", "Status", "Type", "Created"}

    def __init__(self, filename: Path):
        """Init object from an open YEP file object.

        yep_file is full text of the YEP file, filename is path of the YEP file, author_lookup is author exceptions file

        """
        self.filename: Path = filename

        # Parse the headers.
        yep_text = filename.read_text(encoding="utf-8")
        metadata = HeaderParser().parsestr(yep_text)
        required_header_misses = YEP.required_headers - set(metadata.keys())
        if required_header_misses:
            _raise_yep_error(self, f"YEP is missing required headers {required_header_misses}")

        try:
            self.number = int(metadata["YEP"])
        except ValueError:
            _raise_yep_error(self, "YEP number isn't an integer")

        # Check YEP number matches filename
        if self.number != int(filename.stem[4:]):
            _raise_yep_error(self, f"YEP number does not match file name ({filename})", yep_num=True)

        # Title
        self.title: str = metadata["Title"]

        # Type
        self.yep_type: str = metadata["Type"]
        if self.yep_type not in TYPE_VALUES:
            _raise_yep_error(self, f"{self.yep_type} is not a valid Type value", yep_num=True)

        # Status
        status = metadata["Status"]
        if status in SPECIAL_STATUSES:
            status = SPECIAL_STATUSES[status]
        if status not in STATUS_VALUES:
            _raise_yep_error(self, f"{status} is not a valid Status value", yep_num=True)

        # Special case for Active YEPs.
        if status == STATUS_ACTIVE and self.yep_type not in ACTIVE_ALLOWED:
            msg = "Only Process and Informational YEPs may have an Active status"
            _raise_yep_error(self, msg, yep_num=True)

        # Special case for Provisional YEPs.
        if status == STATUS_PROVISIONAL and self.yep_type != TYPE_STANDARDS:
            msg = "Only Standards Track YEPs may have a Provisional status"
            _raise_yep_error(self, msg, yep_num=True)
        self.status: str = status

        # Parse YEP authors
        self.authors: list[_Author] = _parse_author(metadata["Author"])
        if not self.authors:
            raise _raise_yep_error(self, "no authors found", yep_num=True)

        # Topic (for sub-indices)
        _topic = metadata.get("Topic", "").lower().split(",")
        self.topic: set[str] = {topic for topic_raw in _topic if (topic := topic_raw.strip())}

        # Other headers
        self.created = metadata["Created"]
        self.discussions_to = metadata["Discussions-To"]
        self.yocto_version = metadata["Yocto-Version"]
        self.replaces = metadata["Replaces"]
        self.requires = metadata["Requires"]
        self.resolution = metadata["Resolution"]
        self.superseded_by = metadata["Superseded-By"]
        if metadata["Post-History"]:
            # Squash duplicate whitespace
            self.post_history = " ".join(metadata["Post-History"].split())
        else:
            self.post_history = None

    def __repr__(self) -> str:
        return f"<YEP {self.number:0>4} - {self.title}>"

    def __lt__(self, other: YEP) -> bool:
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    @property
    def _author_names(self) -> Iterable[str]:
        """An iterator of the authors' full names."""
        return (author.full_name for author in self.authors)

    @property
    def shorthand(self) -> str:
        """Return reStructuredText tooltip for the YEP type and status."""
        type_code = self.yep_type[0].upper()
        if self.status in HIDE_STATUS:
            return f":abbr:`{type_code} ({self.yep_type}, {self.status})`"
        status_code = self.status[0].upper()
        return f":abbr:`{type_code}{status_code} ({self.yep_type}, {self.status})`"

    @property
    def details(self) -> dict[str, str | int]:
        """Return the line entry for the YEP."""
        return {
            "number": self.number,
            "title": self.title,
            # a tooltip representing the type and status
            "shorthand": self.shorthand,
            # the comma-separated list of authors
            "authors": ", ".join(self._author_names),
            # The targeted Yocto-Version (if present) or the empty string
            "yocto_version": self.yocto_version or "",
        }

    @property
    def full_details(self) -> dict[str, str | int | Sequence[str]]:
        """Returns all headers of the YEP as a dict."""
        return {
            "number": self.number,
            "title": self.title,
            "authors": ", ".join(self._author_names),
            "discussions_to": self.discussions_to,
            "status": self.status,
            "type": self.yep_type,
            "topic": ", ".join(sorted(self.topic)),
            "created": self.created,
            "yocto_version": self.yocto_version,
            "post_history": self.post_history,
            "resolution": self.resolution,
            "requires": self.requires,
            "replaces": self.replaces,
            "superseded_by": self.superseded_by,
            # extra non-header keys for use in ``yeps.json``
            "author_names": tuple(self._author_names),
            "url": f"https://JPEWdev.github.io/yeps/yep-{self.number:0>4}/",
        }


def _raise_yep_error(yep: YEP, msg: str, yep_num: bool = False) -> None:
    if yep_num:
        raise YEPError(msg, yep.filename, yep_number=yep.number)
    raise YEPError(msg, yep.filename)


jr_placeholder = ",Jr"


def _parse_author(data: str) -> list[_Author]:
    """Return a list of author names and emails."""

    author_list = []
    data = (data.replace("\n", " ")
                .replace(", Jr", jr_placeholder)
                .rstrip().removesuffix(","))
    for author_email in data.split(", "):
        if ' <' in author_email:
            author, email = author_email.removesuffix(">").split(" <")
        else:
            author, email = author_email, ""

        author = author.strip()
        if author == "":
            raise ValueError("Name is empty!")

        author = author.replace(jr_placeholder, ", Jr")
        email = email.lower()
        author_list.append(_Author(author, email))
    return author_list
