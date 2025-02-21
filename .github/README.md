# GitHub App Usage in Workflows

## Commit to Main Bot
These workflows use the `Commit to Main Bot` app to commit changes directly to the `main` branch of the repository. The app has been given an exception to bypass the branch protections present on that branch.

### Permissions
This app has been granted `read and write` access to the contents of the repository and `read-only` access to the metadata of the repository (which is the default for GitHub apps and mandatory). All other Organization, Account, and Optional features have not been granted or left as default. Copilot integration has not been enabled.

### Authentication
The private key for this app that is used in this repository was generated on 02/19/2025 and can be accessed in workflows through the `COMMIT_BOT_KEY` repository secret. The app ID is also stored as a Reopository variable under `COMMIT_BOT_ID`.

### Used In

- update_metadata_dictionary.yml
