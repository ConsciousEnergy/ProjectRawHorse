# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.4.x   | Yes                |
| < 0.4   | No                 |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, report them via one of the following:

1. **GitHub Security Advisories** (preferred): [Create a private advisory](https://github.com/ConsciousEnergy/ProjectRawHorse/security/advisories/new)
2. **Email**: consciousenergy@proton.me

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if you have one)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix or mitigation**: Dependent on severity, but we aim for:
  - Critical: 48 hours
  - High: 1 week
  - Medium/Low: Next release cycle

### What Counts as a Security Issue

- Authentication or authorization bypass
- Data injection (SQL injection, XSS, etc.)
- Exposure of sensitive data (GitHub tokens, credentials)
- Denial of service vulnerabilities
- Dependency vulnerabilities with known exploits

### What Does NOT Count

- Bugs that don't have a security impact
- Feature requests
- Data accuracy concerns (use regular issues for these)
- Publicly available data already in the database

## Security Design

Project RawHorse is designed with these security principles:

- **Local-first**: All data processing happens on the user's machine by default
- **No telemetry**: No analytics, tracking, or external data collection
- **Encrypted tokens**: GitHub tokens are stored encrypted at rest
- **Optional auth**: JWT authentication is disabled by default for local use
- **AGPL license**: Full source transparency — anyone can audit the code

## Responsible Disclosure

We follow responsible disclosure practices. If you report a vulnerability:

- We will not take legal action against you for the report
- We will work with you to understand and resolve the issue
- We will credit you in the fix (unless you prefer anonymity)
- We ask that you allow us reasonable time to address the issue before public disclosure

Thank you for helping keep Project RawHorse and its users safe.
