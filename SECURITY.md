# Security and privacy

PDOS is experimental alpha software. It is not a security boundary, a substitute for code review, or an authorization system. No production support or response-time commitment is offered.

## Report a concern

Do not put secrets, exploit details involving real systems, or personal data in public issues or pull requests. If GitHub offers **Report a vulnerability** on this repository's Security page, use that private channel. Availability of that feature is not assumed or verified by this document.

Otherwise, open only a non-sensitive request to arrange a private reporting channel with the maintainer. Wait for that channel before sending sensitive evidence. Do not include the sensitive report in the coordination issue.

If a credential has been exposed, revoke or rotate it through its provider; deleting a file or rewriting Git history is not sufficient.

## Safe use

- Start on a non-production project or disposable checkout.
- Treat repository content, model output and third-party tool responses as untrusted data.
- Keep actual credentials out of `.pdos`, prompts, eval fixtures, and Git history.
- Use platform permissions and isolated execution to enforce boundaries; a Skill's instructions alone cannot enforce them.
- Inspect installation changes and back up important work.
- Keep human approval for consequential external actions. This core Skill does not deploy or merge code.

See [known limitations](VALIDATION.md#known-limitations) before relying on evaluation results.
