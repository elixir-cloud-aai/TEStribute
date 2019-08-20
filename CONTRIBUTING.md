# Contributing

Your contributions are welcome and necessary. Please use [GitHub's issue
tracker] to:

- Report bugs
- Propose or implement features
- Submit code changes / fixes
- Discuss code

Please adhere to the [Code of Conduct].

Please *do not* ask usage questions, installation problems (unless they appear
to be bugs) etc. via the GitHub issue tracker. We will set up a dedicated Q&A
channel soon.

## Reporting bugs

Please use the [project's issue tracker][2] to report bugs. If you have no
experience in filing bug reports, see e.g., these [recommendations by the
Mozilla Developer Network] first. Briefly, it is important that bug reports
contain enough detail, background and, if applicable, _minimal_ reproducible
sample code. Tell us what you expect to happen, and what actually does happen.

## Implementing features and submitting fixes

Kindly use pull requests to submit changes to the code base. But please note
that this project is driven by a community that likes to act on consensus. So
in your own best interest, before just firing off a pull request after a lot of
work, please [open an issue][2] to **discuss your proposed changes first**.
Afterwards, please stick to the following simple rules to make sure your pull
request will indeed be merged:

1. Fork the repo and create a [_feature branch_] from branch `dev`, if present,
   or `master`.
2. If you've added code that should be tested, add tests.
3. Ensure that all tests pass.
4. Document your code and update all relevant documentation.
5. Stick to the code and documentation style (see below).
6. Issue the pull request.

Important: Note that all your contributions are understood to be covered by the
[same license][1] that covers the entire project.

## Code & documentation style

### Python

Please use a recent version of Python 3.6 or higher. Python code, docstring and
comment style loosely follows the [Google Python Style Guide]. Please try to
conform to the used style to maintain consistency. Include [type
hints/annotations] at least for function/method signatures.

Please use **all** of the following linters and validation tools with default
settings and ensure that no warnings/errors are reported in any files before you
commit:

- [`pylint`]
- [`flake8`]
- [`mypy`]

[1]: LICENSE
[2]: <https://github.com/elixir-europe/TEStribute/issues/>
[Code of Conduct]: CODE_OF_CONDUCT.md
[_feature branch_]: <https://datasift.github.io/gitflow/IntroducingGitFlow.html>
[`flake8`]: <https://gitlab.com/pycqa/flake8>
[GitHub's issue tracker]: <https://guides.github.com/features/issues/>
[Google Python Style Guide]: <https://github.com/google/styleguide/blob/gh-pages/pyguide.md>
[`mypy`]: <https://github.com/python/mypy>
[`pylint`]: <https://github.com/PyCQA/pylint>
[recommendations by the Mozilla Developer Network]: <https://developer.mozilla.org/en-US/docs/Mozilla/QA/Bug_writing_guidelines>
[short tutorial]: <https://guides.github.com/features/issues/>
[type hints/annotations]: <https://docs.python.org/3.7/library/typing.html>
