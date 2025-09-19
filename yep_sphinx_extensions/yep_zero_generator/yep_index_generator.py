"""Automatically create YEP 0 (the YEP index),

This file generates and writes the YEP index to disk, ready for later
processing by Sphinx. Firstly, we parse the individual YEP files, getting the
RFC2822 header, and parsing and then validating that metadata.

After collecting and validating all the YEP data, the creation of the index
itself is in three steps:

    1. Output static text.
    2. Format an entry for the YEP.
    3. Output the YEP (both by the category and numerical index).

We then add the newly created YEP 0 file to two Sphinx environment variables
to allow it to be processed as normal.

"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from yep_sphinx_extensions.yep_zero_generator import parser
from yep_sphinx_extensions.yep_zero_generator import subindices
from yep_sphinx_extensions.yep_zero_generator import writer
from yep_sphinx_extensions.yep_zero_generator.constants import SUBINDICES_BY_TOPIC

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def _parse_yeps(path: Path) -> list[parser.YEP]:
    # Read from root directory
    yeps: list[parser.YEP] = []

    for file_path in path.iterdir():
        if not file_path.is_file():
            continue  # Skip directories etc.
        if file_path.match("yep-0000*"):
            continue  # Skip pre-existing YEP 0 files
        if file_path.match("yep-????.rst"):
            yep = parser.YEP(path.joinpath(file_path).absolute())
            yeps.append(yep)

    return sorted(yeps)


def create_yep_json(yeps: list[parser.YEP]) -> str:
    return json.dumps({yep.number: yep.full_details for yep in yeps}, indent=1)


def write_yeps_json(yeps: list[parser.YEP], path: Path) -> None:
    # Create yeps.json
    json_yeps = create_yep_json(yeps)
    Path(path, "yeps.json").write_text(json_yeps, encoding="utf-8")
    os.makedirs(os.path.join(path, "api"), exist_ok=True)
    Path(path, "api", "yeps.json").write_text(json_yeps, encoding="utf-8")


def create_yep_zero(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    yeps = _parse_yeps(Path(app.srcdir))

    numerical_index_text = writer.YEPZeroWriter().write_numerical_index(yeps)
    subindices.update_sphinx("numerical", numerical_index_text, docnames, env)

    yep0_text = writer.YEPZeroWriter().write_yep0(yeps, builder=env.settings["builder"])
    yep0_path = subindices.update_sphinx("yep-0000", yep0_text, docnames, env)
    yeps.append(parser.YEP(yep0_path))

    subindices.generate_subindices(SUBINDICES_BY_TOPIC, yeps, docnames, env)

    write_yeps_json(yeps, Path(app.outdir))
