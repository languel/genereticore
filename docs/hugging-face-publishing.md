# Local Hugging Face publishing

Browser sign-in and local CLI/SDK sign-in are separate. GeneretiCore publishes to
the `languel` Hugging Face account, matching its `languel` GitHub home.
Public student downloads use anonymous reads and need no account or token.

## One-time login

1. Sign in as `languel` at https://huggingface.co/settings/tokens.
2. Create a token named **GeneretiCore publishing** with **Write** permission.
   This permits creating and publishing your own model repositories. A scoped
   fine-grained token is also suitable once its repository permissions allow
   the intended publishing operations.
3. In a local terminal run `hf auth login --force`. Paste the token only into
   the hidden prompt. Keep Git credential storage off for SDK/CLI publishing.
4. Run `hf auth whoami`; the account should be `languel`.

The CLI is already installed on this Mac at `~/.local/bin/hf`. Saved login is
shared by the Hub CLI and Python SDK through their standard credential store.
Never put a token in a command argument, workflow, project file, issue, or chat.
Creating/pasting a credential is a user step; agents can use the saved login.

## Publishing converted bundles

Keep all model packages and staging files outside the code checkout. Convert
using the pinned contributor environment (coremltools 8.3.0, torch 2.5.1,
diffusers 0.32.2). `scripts/convert_native_images.py` accepts `--size 256` or
`--size 512` and a required external `--output-root`. Run the SDXS base conversion,
then `--control` for sketch, then `--family sd-turbo` for Turbo. The shared SDXS
encoder/decoder/base UNet are required by the Turbo runtime too.

`python scripts/image_bundle.py prepare EXTERNAL_MODEL_ROOT EXTERNAL_STAGING
--family sdxs --sizes 256 512` prepares a contributor bundle. Repeat with
`--family sd-turbo` and a different staging folder. The preparer initially labels
staging as private pending review. Before a public upload retain the reviewed
Notice.txt, upstream credits/backlinks, full license copies and provenance,
and regenerate the checksum manifest after any documentation edits.

Test native inference at each resolution before publishing. Then use
`python scripts/image_bundle.py upload EXTERNAL_STAGING
languel/genereticore-sdxs-coreml --public` (or the Turbo repo). This uses the saved
login. Public updates require retained notices and explicit `--public`.

After an upload, pin the returned commit SHA, manifest SHA-256 and exact byte
count in both `docs/image-bundles.json` and `genereticore/image/bundles.json`.
Update authored references under `help/docs`, run
`python scripts/sync_node_references.py`, and verify an anonymous clean download.
Do not replace a published pin until its files and installation have passed.

## Moving between personal accounts

Hugging Face does not support directly transferring from one personal account
to another. Use `hf repos duplicate SOURCE DESTINATION --public` while logged in
as the destination account. This copies the model repository on the Hub without
uploading the local weight files again. Update publisher links/model cards,
regenerate any affected checksum manifest, and update every Comfy download pin.
The supported automated preparation is `scripts/migrate_image_repos.py`.

Keep the source until the destination is public, complete, checksum-verified and
usable anonymously. To retire the source, switch to its owning saved login,
verify `hf auth whoami`, then delete only the specifically verified old repos.
Return to the main `languel` publishing login afterward. GitHub repositories do
not need moving: GeneretiCore already belongs to `languel` there.

Official documentation: [Hub login](https://huggingface.co/docs/huggingface_hub/guides/cli#hf-auth-login),
[repository transfer limits](https://huggingface.co/docs/hub/repositories-settings#renaming-or-transferring-a-repo).


## Troubleshooting local login

If login reports `FileNotFoundError` from `os.getcwd()`, your terminal's current
folder was removed. Run `cd ~` (or enter an existing project folder), then activate
the already saved login with `hf auth switch --token-name GeneretiCore
--no-add-to-git-credential`. No new token is needed if it was already validated
and saved.

If `hf auth whoami` still shows another account, an inherited `HF_TOKEN` can
override the saved login. For this setup use `env -u HF_TOKEN hf auth whoami` and
prefix SDK publishing commands with `env -u HF_TOKEN`. This uses the saved login
without reading, printing or changing the environment credential. If you manage
your own shell setup, remove its obsolete override separately. The desired saved
login is named `GeneretiCore`. The old liuboto model copies were deleted after
verification; their saved publishing login is no longer available locally.
