# Security Policy for `markpickle`

## Introduction

Thank you for your interest in the security of this project. As an open-source side project maintained by a single
individual, I take security seriously and appreciate the community's help in keeping it safe.

This document outlines how to report vulnerabilities and provides guidance on how you can manage security in your own
usage of this tool. Please understand that this is not a commercial product, so there is no dedicated security team on
standby. Reports are handled on a best-effort basis, similar to any other bug report.

## Supported Versions

Security updates will only be applied to the **most recent major/minor version** available on PyPI. Please ensure you
are using the latest release to receive security patches.

| Version | Supported            |
|---------|----------------------|
| `1.x.x` | :white\_check\_mark: |
| `< 1.0` | :x:                  |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately. **Do not create a public GitHub issue.**

Instead, please email me at **`matthewdeanmartin@gmail.com`**.

When reporting, please include the following to help me understand and address the issue quickly:

* The version of the tool you are using.
* A clear description of the vulnerability.
* Steps to reproduce the vulnerability, if possible.
* Any potential impact you've identified.

I will do my best to acknowledge your report within a few days and keep you updated on the progress of any fix. Once a
fix is released, I will credit you for the discovery unless you prefer to remain anonymous.

## Dependency Management

This tool, like most Python projects, relies on third-party libraries.

### For Library Users

If you are using this project as a library, you are responsible for managing and auditing your own dependencies. Tools
like `pip-audit`, `snyk`, or GitHub's Dependabot can help you identify known vulnerabilities in your dependency tree.

### For Application Users (CLI)

The application may ship with pinned dependencies for reproducibility. If you discover that a pinned *transitive
dependency* (a dependency of one of our dependencies) has a known vulnerability, you have a few options:

1. **Override the Dependency:** In your own Python environment, you can force an upgrade of the vulnerable
   sub-dependency. For example, if a library `some-lib` is vulnerable, you can create a `requirements.txt` file with
   `some-lib>=1.2.4` and install it alongside this tool.
2. **Submit an Issue or Pull Request:** Please open an issue on the GitHub repository notifying me of the vulnerability.
   A pull request that updates the dependency and confirms that all tests still pass is the fastest way to get it fixed
   and is greatly appreciated.

## Secure Usage Recommendations

This tool is designed to analyze code and metadata from local files and public package indexes. It does not execute any
code from the repositories it analyzes. However, for maximum safety and isolation, you should run all tools
inside a container.

### Running with Docker

You can containerize this application to isolate it from your host system. Here is a sample `Dockerfile` you can use as
a starting point:

```dockerfile
# Use a minimal, secure base image
FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# Create a non-root user for security
RUN useradd --create-home appuser
USER appuser

# Copy only the necessary files for installation
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies in a virtual environment owned by the non-root user
# This prevents pip from running as root
RUN python -m venv /home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

# Install the project and its dependencies
# Use --no-cache-dir to keep the image size down
RUN pip install --no-cache-dir .

# Copy the application source code
COPY --chown=appuser:appuser markpickle/ ./markpickle/

# Set the entrypoint to run the tool
ENTRYPOINT ["markpickle"]
CMD ["--help"]
```

**To build and run this container:**

```bash
# Build the image
docker build -t markpickle .

# Run the tool against a local repository mounted into the container
# This command mounts your current directory into /data inside the container
docker run --rm -v "$(pwd):/data" markpickle /data
```

This approach ensures the tool only has access to the repository you explicitly provide and cannot interfere with other
parts of your system.