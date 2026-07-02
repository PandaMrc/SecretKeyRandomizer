# Security Notes

SecretKeyRandomizer is a generator, not a secret manager. It creates new secret
values using cryptographically secure randomness and does not store them.

Use a proper secret storage system for long-term storage, rotation, access
control, and audit requirements.

Avoid placing generated secrets in public repositories, frontend bundles, logs,
screenshots, chat messages, crash reports, or analytics events.
