# Support

FAS-Bench is a benchmark and research-engineering project. Use the channel that matches the problem.

## Before opening an issue

1. Read [README.md](README.md).
2. Check the [documentation index](docs/README.md).
3. Search existing issues and pull requests.
4. Run `fas-bench benchmark doctor` where applicable.

## Usage and methodology questions

For installation, CLI usage, benchmark concepts, or methodology questions, open a normal GitHub issue with:

- the FAS-Bench version or commit;
- Python version and operating system;
- the exact command;
- expected behavior;
- actual behavior;
- a minimal reproducible example.

For benchmark semantics, reference the relevant section of [docs/specification.md](docs/specification.md).

## Bugs

Use the bug issue form. Include reproducible steps and structured output where possible.

Do not include:

- credentials;
- private keys;
- hidden benchmark cases;
- evaluator-only material;
- sensitive production data.

## Security and integrity

Do **not** use a public issue for sandbox escapes, oracle compromise, hidden-data leakage, credential exposure, release-integrity issues, or other security vulnerabilities.

Follow [SECURITY.md](SECURITY.md).

## Contributions

Feature proposals and benchmark changes should explain the security objective, expected semantics, validation strategy, and compatibility impact. See [CONTRIBUTING.md](CONTRIBUTING.md).
