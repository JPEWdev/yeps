"""Code to handle the output of YEP 0."""

from __future__ import annotations

from typing import TYPE_CHECKING
import unicodedata

from yep_sphinx_extensions.yep_processor.transforms.yep_headers import ABBREVIATED_STATUSES
from yep_sphinx_extensions.yep_processor.transforms.yep_headers import ABBREVIATED_TYPES
from yep_sphinx_extensions.yep_zero_generator.constants import DEAD_STATUSES
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_ACCEPTED
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_ACTIVE
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_DEFERRED
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_DRAFT
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_FINAL
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_PROVISIONAL
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_REJECTED
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_VALUES
from yep_sphinx_extensions.yep_zero_generator.constants import STATUS_WITHDRAWN
from yep_sphinx_extensions.yep_zero_generator.constants import SUBINDICES_BY_TOPIC
from yep_sphinx_extensions.yep_zero_generator.constants import TYPE_INFO
from yep_sphinx_extensions.yep_zero_generator.constants import TYPE_PROCESS
from yep_sphinx_extensions.yep_zero_generator.constants import TYPE_VALUES
from yep_sphinx_extensions.yep_zero_generator.errors import YEPError

if TYPE_CHECKING:
    from yep_sphinx_extensions.yep_zero_generator.parser import YEP

HEADER = """\
YEP: 0
Title: Index of Yocto Enhancement Proposals (YEPs)
Author: The YEP Editors
Status: Active
Type: Informational
Content-Type: text/x-rst
Created: 13-Jul-2000
"""

INTRO = """\
This YEP contains the index of all Yocto Enhancement Proposals,
known as YEPs.  YEP numbers are :yep:`assigned <1#yep-editors>`
by the YEP editors, and once assigned are never changed.  The
`version control history <https://github.com/JPEWdev/yeps>`_ of
the YEP texts represent their historical record.
"""


class YEPZeroWriter:
    # This is a list of reserved YEP numbers.  Reservations are not to be used for
    # the normal YEP number allocation process - just give out the next available
    # YEP number.  These are for "special" numbers that may be used for semantic,
    # humorous, or other such reasons, e.g. 401, 666, 754.
    #
    # YEP numbers may only be reserved with the approval of a YEP editor.  Fields
    # here are the YEP number being reserved and the claimants for the YEP.
    # Although the output is sorted when YEP 0 is generated, please keep this list
    # sorted as well.
    RESERVED = dict()

    def __init__(self):
        self.output: list[str] = []

    def emit_text(self, content: str) -> None:
        # Appends content argument to the output list
        self.output.append(content)

    def emit_newline(self) -> None:
        self.output.append("")

    def emit_author_table_separator(self, max_name_len: int) -> None:
        author_table_separator = "=" * max_name_len + "  " + "=" * len("email address")
        self.output.append(author_table_separator)

    def emit_yep_row(
        self,
        *,
        shorthand: str,
        number: int,
        title: str,
        authors: str,
        yocto_version: str | None = None,
    ) -> None:
        self.emit_text(f"   * - {shorthand}")
        self.emit_text(f"     - :yep:`{number} <{number}>`")
        self.emit_text(f"     - :yep:`{title.replace('`', '')} <{number}>`")
        self.emit_text(f"     - {authors}")
        if yocto_version is not None:
            self.emit_text(f"     - {yocto_version}")

    def emit_column_headers(self, *, include_version=True) -> None:
        """Output the column headers for the YEP indices."""
        self.emit_text(".. list-table::")
        self.emit_text("   :header-rows: 1")
        self.emit_text("   :widths: auto")
        self.emit_text("   :class: yep-zero-table")
        self.emit_newline()
        self.emit_text("   * - ")
        self.emit_text("     - YEP")
        self.emit_text("     - Title")
        self.emit_text("     - Authors")
        if include_version:
            self.emit_text("     - ")  # for Yocto-Version

    def emit_title(self, text: str, *, symbol: str = "=") -> None:
        self.output.append(text)
        self.output.append(symbol * len(text))
        self.emit_newline()

    def emit_subtitle(self, text: str) -> None:
        self.emit_title(text, symbol="-")

    def emit_table(self, yeps: list[YEP]) -> None:
        include_version = any(yep.details["yocto_version"] for yep in yeps)
        self.emit_column_headers(include_version=include_version)
        for yep in yeps:
            details = yep.details
            if not include_version:
                details.pop("yocto_version")
            self.emit_yep_row(**details)

    def emit_yep_category(self, category: str, yeps: list[YEP]) -> None:
        self.emit_subtitle(category)
        self.emit_table(yeps)
        # list-table must have at least one body row
        if len(yeps) == 0:
            self.emit_text("   * -")
            self.emit_text("     -")
            self.emit_text("     -")
            self.emit_text("     -")
            self.emit_text("     -")
        self.emit_newline()

    def write_numerical_index(self, yeps: list[YEP]) -> str:
        """Write YEPs by number."""
        self.emit_text(".. _numerical-index:")
        self.emit_newline()

        self.emit_title("Numerical Index")
        self.emit_table(yeps)
        self.emit_newline()

        numerical_index_string = "\n".join(self.output)
        return numerical_index_string

    def write_yep0(
        self,
        yeps: list[YEP],
        header: str = HEADER,
        intro: str = INTRO,
        is_yep0: bool = True,
        builder: str = None,
    ) -> str:
        # YEP metadata
        self.emit_text(header)
        self.emit_newline()

        if len(yeps) == 0:
            yep0_string = "\n".join(self.output)
            return yep0_string

        # Introduction
        self.emit_title("Introduction")
        self.emit_text(intro)
        self.emit_newline()

        # YEPs by topic
        if is_yep0:
            self.emit_title("Topics")
            self.emit_text(
                "YEPs for specialist subjects are :doc:`indexed by topic <topic/index>`."
            )
            self.emit_newline()
            for subindex in SUBINDICES_BY_TOPIC:
                target = (
                    f"topic/{subindex}.html"
                    if builder == "html"
                    else f"../topic/{subindex}/"
                )
                self.emit_text(f"* `{subindex.title()} YEPs <{target}>`_")
                self.emit_newline()
            self.emit_newline()

            self.emit_title("API")
            self.emit_text(
                "The `YEPS API <https://JPEWdev.github.io/yeps/api/yeps.json>`__ is a JSON file of metadata about "
                "all the published YEPs. :doc:`Read more here <api/index>`."
            )
            self.emit_newline()

        # YEPs by number
        if is_yep0:
            self.emit_title("Numerical Index")
            self.emit_text(
                "The :doc:`numerical index </numerical>` contains "
                "a table of all YEPs, ordered by number."
            )
            self.emit_newline()

        # YEPs by category
        self.emit_title("Index by Category")
        meta, info, provisional, accepted, open_, finished, historical, deferred, dead = _classify_yeps(yeps)
        yep_categories = [
            ("Process and Meta-YEPs", meta),
            ("Other Informational YEPs", info),
            ("Provisional YEPs (provisionally accepted; interface may still change)", provisional),
            ("Accepted YEPs (accepted; may not be implemented yet)", accepted),
            ("Open YEPs (under consideration)", open_),
            ("Finished YEPs (done, with a stable interface)", finished),
            ("Historical Meta-YEPs and Informational YEPs", historical),
            ("Deferred YEPs (postponed pending further research or updates)", deferred),
            ("Rejected, Superseded, and Withdrawn YEPs", dead),
        ]
        for (category, yeps_in_category) in yep_categories:
            # For sub-indices, only emit categories with entries.
            # For YEP 0, emit every category, but only with a table when it has entries.
            if len(yeps_in_category) > 0:
                self.emit_yep_category(category, yeps_in_category)
            elif is_yep0:
                # emit the category with no table
                self.emit_subtitle(category)
                self.emit_text("None.")
                self.emit_newline()

        self.emit_newline()

        # Reserved YEP numbers
        if is_yep0 and self.RESERVED:
            self.emit_title("Reserved YEP Numbers")
            self.emit_column_headers(include_version=False)
            for number, claimants in sorted(self.RESERVED.items()):
                self.emit_yep_row(
                    shorthand="",
                    number=number,
                    title="RESERVED",
                    authors=claimants,
                    yocto_version=None,
                )

            self.emit_newline()

        # YEP types key
        self.emit_title("YEP Types Key")
        for type_ in sorted(TYPE_VALUES):
            self.emit_text(
                f"* **{type_[0]}** --- *{type_}*: {ABBREVIATED_TYPES[type_]}"
            )
            self.emit_newline()

        self.emit_text(":yep:`More info in YEP 1 <1#yep-types>`.")
        self.emit_newline()

        # YEP status key
        self.emit_title("YEP Status Key")
        for status in sorted(STATUS_VALUES):
            # Draft YEPs have no status displayed, Active shares a key with Accepted
            status_code = "<No letter>" if status == STATUS_DRAFT else status[0]
            self.emit_text(
                f"* **{status_code}** --- *{status}*: {ABBREVIATED_STATUSES[status]}"
            )
            self.emit_newline()

        self.emit_text(":yep:`More info in YEP 1 <1#yep-review-resolution>`.")
        self.emit_newline()

        if is_yep0:
            # YEP owners
            authors_dict = _verify_email_addresses(yeps)
            max_name_len = max(len(author_name) for author_name in authors_dict)
            self.emit_title("Authors/Owners")
            self.emit_author_table_separator(max_name_len)
            self.emit_text(f"{'Name':{max_name_len}}  Email Address")
            self.emit_author_table_separator(max_name_len)
            for author_name in _sort_authors(authors_dict):
                # Use the email from authors_dict instead of the one from "author" as
                # the author instance may have an empty email.
                self.emit_text(f"{author_name:{max_name_len}}  {authors_dict[author_name]}")
            self.emit_author_table_separator(max_name_len)
            self.emit_newline()
            self.emit_newline()

        yep0_string = "\n".join(self.output)
        return yep0_string


def _classify_yeps(yeps: list[YEP]) -> tuple[list[YEP], ...]:
    """Sort YEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    meta = []
    info = []
    provisional = []
    accepted = []
    open_ = []
    finished = []
    historical = []
    deferred = []
    dead = []
    for yep in yeps:
        # Order of 'if' statement important.  Key Status values take precedence
        # over Type value, and vice-versa.
        if yep.status == STATUS_DRAFT:
            open_.append(yep)
        elif yep.status == STATUS_DEFERRED:
            deferred.append(yep)
        elif yep.yep_type == TYPE_PROCESS:
            if yep.status in {STATUS_ACCEPTED, STATUS_ACTIVE}:
                meta.append(yep)
            elif yep.status in {STATUS_WITHDRAWN, STATUS_REJECTED}:
                dead.append(yep)
            else:
                historical.append(yep)
        elif yep.status in DEAD_STATUSES:
            dead.append(yep)
        elif yep.yep_type == TYPE_INFO:
            # Hack until the conflict between the use of "Final"
            # for both API definition YEPs and other (actually
            # obsolete) YEPs is addressed
            if yep.status == STATUS_ACTIVE or "release schedule" not in yep.title.lower():
                info.append(yep)
            else:
                historical.append(yep)
        elif yep.status == STATUS_PROVISIONAL:
            provisional.append(yep)
        elif yep.status in {STATUS_ACCEPTED, STATUS_ACTIVE}:
            accepted.append(yep)
        elif yep.status == STATUS_FINAL:
            finished.append(yep)
        else:
            raise YEPError(f"Unsorted ({yep.yep_type}/{yep.status})", yep.filename, yep.number)
    return meta, info, provisional, accepted, open_, finished, historical, deferred, dead


def _verify_email_addresses(yeps: list[YEP]) -> dict[str, str]:
    authors_dict: dict[str, set[str]] = {}
    for yep in yeps:
        for author in yep.authors:
            # If this is the first time we have come across an author, add them.
            if author.full_name not in authors_dict:
                authors_dict[author.full_name] = set()

            # If the new email is an empty string, move on.
            if not author.email:
                continue
            # If the email has not been seen, add it to the list.
            authors_dict[author.full_name].add(author.email)

    valid_authors_dict: dict[str, str] = {}
    too_many_emails: list[tuple[str, set[str]]] = []
    for full_name, emails in authors_dict.items():
        if len(emails) > 1:
            too_many_emails.append((full_name, emails))
        else:
            valid_authors_dict[full_name] = next(iter(emails), "")
    if too_many_emails:
        err_output = []
        for author, emails in too_many_emails:
            err_output.append(" " * 4 + f"{author}: {emails}")
        raise ValueError(
            "some authors have more than one email address listed:\n"
            + "\n".join(err_output)
        )

    return valid_authors_dict


def _sort_authors(authors_dict: dict[str, str]) -> list[str]:
    return sorted(authors_dict, key=_author_sort_by)


def _author_sort_by(author_name: str) -> str:
    """Skip lower-cased words in surname when sorting."""
    surname, *_ = author_name.split(",")
    surname_parts = surname.split()
    for i, part in enumerate(surname_parts):
        if part[0].isupper():
            base = " ".join(surname_parts[i:]).lower()
            return unicodedata.normalize("NFKD", base)
    # If no capitals, use the whole string
    return unicodedata.normalize("NFKD", surname.lower())
