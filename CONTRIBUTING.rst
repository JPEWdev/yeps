Contributing Guidelines
=======================

To learn more about the purpose of YEPs and how to go about writing one, please
start reading at `YEP 1 <https://JPEWdev.github.io/yeps/yep-0001/>`_.
Also, make sure to check the `README <./README.rst>`_ for information
on how to render the YEPs in this repository.
Thanks again for your contributions, and we look forward to reviewing them!


Before writing a new YEP
------------------------

Prior to submitting a pull request here with your draft YEP, see `YEP 1
<https://JPEWdev.github.io/yeps/yep-0001/#start-with-an-idea-for-python>`_
for some important steps to consider, including proposing and discussing it
first in an appropriate venue, drafting a YEP and gathering feedback, and
developing at least a prototype reference implementation of your idea.


Contributing changes to existing YEPs
-------------------------------------

In general, most non-Draft/Active YEPs are considered to be historical
documents rather than living specifications or documentation. Major changes to
their core content usually require a new YEP, while smaller modifications may
or may not be appropriate, depending on the YEP's status. See `YEP Maintenance
<https://JPEWdev.github.io/yeps/yep-0001/#yep-maintenance>`_
and `Changing Existing YEPs
<https://JPEWdev.github.io/yeps/yep-0001/#changing-existing-yeps>`_ in YEP 1 for more.

Copyediting and proofreading Draft and Active YEPs is welcome (subject to
review by the YEP author), and can be done via pull request to this repo.
Substantive content changes should first be proposed on YEP discussion threads.
We do advise against PRs that simply mass-correct minor typos on older YEPs
which don't significantly impair meaning and understanding.

If you're still unsure, we encourage you to reach out first before opening a
PR here. For example, you could contact the YEP author(s), propose your idea in
a discussion venue appropriate to the YEP.

Opening a pull request
----------------------

The YEPs repository defines a set of pull request templates, which should be
used when opening a PR.

If you use Git from the command line, you may be accustomed to creating PRs
by following the URL that is provided after pushing a new branch. **Do not use
this link**, as it does not provide the option to populate the PR template.

However, you *can* use the ``gh`` command line tool. ``gh pr create`` will allow
you to create a pull request, will prompt you for the template you wish to use,
and then give you the option of continuing editing in your browser.

Alternatively, after pushing your branch, you can visit
`https://github.com/JPEWdev/yeps <https://github.com/JPEWdev/yeps>`__, and follow
the link in the notification about recent changes to your branch to
create a new PR. The in-browser interface will allow you to select a PR template
for your new PR.

Commit messages and PR titles
-----------------------------

When adding or modifying a YEP, please include the YEP number in the commit
summary and pull request title. For example, ``YEP NNN: <summary of changes>``.
Likewise, prefix rendering infrastructure changes with ``Infra:``, linting
alterations with ``Lint:`` and other non-YEP meta changes, such as updates to
the Readme/Contributing Guide, issue/PR template, etc., with ``Meta:``.

..
    Sign the Contributor License Agreement
    --------------------------------------

    All contributors need to sign the
    `PSF Contributor Agreement <https://www.python.org/psf/contrib/contrib-form/>`_.
    to ensure we legally accept your work.

    You don't need to do anything beforehand;
    go ahead and create your pull request,
    and our bot will ping you to sign the CLA if needed.
    `See the CPython devguide
    <https://devguide.python.org/pullrequest/#licensing>`__
    for more information.

..
    Code of Conduct
    ---------------

    All interactions for this project are covered by the
    `PSF Code of Conduct <https://www.python.org/psf/codeofconduct/>`_. Everyone is
    expected to be open, considerate, and respectful of others, no matter their
    position within the project.


Run pre-commit linting locally
------------------------------

You can run this repo's basic linting suite locally,
either on-demand, or automatically against modified files
whenever you commit your changes.

They are also run in CI, so you don't have to run them locally, though doing
so will help you catch and potentially fix common mistakes before pushing
your changes and opening a pull request.

This repository uses the `pre-commit <https://pre-commit.com/>`_ tool to
install, configure and update a suite of hooks that check for
common problems and issues, and fix many of them automatically.

If your system has ``make`` installed, you can run the pre-commit checkers
on the full repo by running ``make lint``. This will
install pre-commit in the current virtual environment if it isn't already,
so make sure you've activated the environment you want it to use
before running this command.

Otherwise, you can install pre-commit with

.. code-block:: bash

    python -m pip install pre-commit

(or your choice of installer), and then run the hooks on all the files
in the repo with

.. code-block:: bash

    pre-commit run --all-files

or only on any files that have been modified but not yet committed with

.. code-block:: bash

    pre-commit run

If you would like pre-commit to run automatically against any modified files
every time you commit, install the hooks with

.. code-block:: bash

    pre-commit install

Then, whenever you ``git commit``, pre-commit will run and report any issues
it finds or changes it makes, and abort the commit to allow you to check,
and if necessary correct them before committing again.


Check and fix YEP spelling
--------------------------

To check for common spelling mistakes in your YEP and automatically suggest
corrections, you can run the codespell tool through pre-commit as well.

Like the linters, on a system with ``make`` available, it can be installed
(in the currently-activated environment) and run on all files in the
repository with a single command, ``make spellcheck``.

For finer control or on other systems, after installing pre-commit as in
the previous section, you can run it against only the files
you've modified and not yet committed with

.. code-block:: bash

    pre-commit run --hook-stage manual codespell

or against all files with

.. code-block:: bash

    pre-commit run --all-files --hook-stage manual codespell
