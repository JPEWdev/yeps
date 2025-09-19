"""Utilities to support sub-indices for YEPs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from yep_sphinx_extensions.yep_zero_generator import writer

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

    from yep_sphinx_extensions.yep_zero_generator.parser import YEP


def update_sphinx(filename: str, text: str, docnames: list[str], env: BuildEnvironment) -> Path:
    file_path = Path(env.srcdir, f"{filename}.rst")
    file_path.write_text(text, encoding="utf-8")

    # Add to files for builder
    docnames.append(filename)
    # Add to files for writer
    env.found_docs.add(filename)

    return file_path


def generate_subindices(
    subindices: dict[str, str],
    yeps: list[YEP],
    docnames: list[str],
    env: BuildEnvironment,
) -> None:
    # create topic directory
    os.makedirs(os.path.join(env.srcdir, "topic"), exist_ok=True)

    # Create sub index page
    generate_topic_contents(docnames, env)

    for subindex, additional_description in subindices.items():
        header_text = f"{subindex.title()} YEPs"
        header_line = "#" * len(header_text)
        header = header_text + "\n" + header_line + "\n"

        topic = subindex.lower()
        filtered_yeps = [yep for yep in yeps if topic in yep.topic]
        subindex_intro = f"""\
This is the index of all Yocto Enhancement Proposals (YEPs) labelled
under the '{subindex.title()}' topic. This is a sub-index of :yep:`0`,
the YEP index.

{additional_description}
"""
        subindex_text = writer.YEPZeroWriter().write_yep0(
            filtered_yeps, header, subindex_intro, is_yep0=False,
        )
        update_sphinx(f"topic/{subindex}", subindex_text, docnames, env)


def generate_topic_contents(docnames: list[str], env: BuildEnvironment):
    update_sphinx("topic/index", """\
.. _topic-index:

Topic Index
***********

YEPs are indexed by topic on the pages below:

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :glob:

   *
""", docnames, env)
