# State privacy and version control

Use a hybrid policy:

- Commit shared, sanitized product state: `STATE.md`, specs, plans, decisions, reviews, workstreams, and relevant archives.
- Keep machine-local paths, environment identity, or sensitive working notes under `.pdos/private/` or `.pdos/local/`; these paths are ignored by the bundled `.gitignore`.
- Never store passwords, API keys, access tokens, private keys, raw customer personal data, production credentials, or secret environment values anywhere in `.pdos`.
- Summarize sensitive evidence without copying it. Link to an approved secure system when the team needs the source.
- Before committing PDOS files, inspect the diff for secrets, customer data, internal URLs, and stale local paths.

Ignored does not mean secure. Delete material that should not be stored locally at all.
