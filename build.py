#!/usr/bin/env python3
# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""Build script for Sphinx documentation"""

import argparse
import os
from pathlib import Path

from sphinx.application import Sphinx


def create_parser():
    parser = argparse.ArgumentParser(description="Build YEP documents")
    # alternative builders:
    builders = parser.add_mutually_exclusive_group()
    builders.add_argument("-l", "--check-links", action="store_const",
                          dest="builder", const="linkcheck",
                          help='Check validity of links within YEP sources. '
                               'Cannot be used with "-f" or "-d".')
    builders.add_argument("-f", "--build-files", action="store_const",
                          dest="builder", const="html",
                          help='Render YEPs to "yep-NNNN.html" files (default). '
                               'Cannot be used with "-d" or "-l".')
    builders.add_argument("-d", "--build-dirs", action="store_const",
                          dest="builder", const="dirhtml",
                          help='Render YEPs to "index.html" files within "yep-NNNN" directories. '
                               'Cannot be used with "-f" or "-l".')

    parser.add_argument(
        "-o",
        "--output-dir",
        default="build",
        help="Output directory, relative to root. Default 'build'.",
    )

    return parser.parse_args()


def create_index_file(html_root: Path, builder: str) -> None:
    """Copies YEP 0 to the root index.html so that /yeps/ works."""
    yep_zero_file = "yep-0000.html" if builder == "html" else "yep-0000/index.html"
    try:
        yep_zero_text = html_root.joinpath(yep_zero_file).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    if builder == "dirhtml":
        yep_zero_text = yep_zero_text.replace('="../', '="')  # remove relative directory links
    html_root.joinpath("index.html").write_text(yep_zero_text, encoding="utf-8")


if __name__ == "__main__":
    args = create_parser()

    root_directory = Path(__file__).resolve().parent
    source_directory = root_directory / "yeps"
    build_directory = root_directory / args.output_dir

    # builder configuration
    sphinx_builder = args.builder or "html"

    app = Sphinx(
        source_directory,
        confdir=source_directory,
        outdir=build_directory / sphinx_builder,
        doctreedir=build_directory / "doctrees",
        buildername=sphinx_builder,
        warningiserror=True,
        parallel=os.cpu_count() or 1,
        tags=["internal_builder"],
        keep_going=True,
    )
    app.build()

    create_index_file(build_directory, sphinx_builder)
