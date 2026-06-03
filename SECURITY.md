# Security Policy

Report security issues privately to the repository owner.

## Scope

Security-sensitive areas include:

- Docker image build scripts.
- Host wrapper behavior, especially file opening.
- Model download/install tooling.
- Future MCP or remote automation integrations.

## Notes

Do not expose any future MCP server or simulation worker to a public network
without a strict path sandbox. LTspice automation can read and write files and
spawn subprocesses.
