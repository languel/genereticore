# Comfy Registry release record

## 0.1.0 early alpha — October 10, 2026

Published source commit: `c871d66334611cfc41bd05016b70d33c5acef4c8`.
[Successful publishing workflow](https://github.com/languel/genereticore/actions/runs/38073655508).
[Registry package](https://registry.comfy.org/publishers/liuboto/nodes/genereticore).
[Published archive](https://cdn.comfy.org/liuboto/genereticore/0.1.0/node.zip).

The configured repository secret passed the actual authenticated publication.
No credential value was inspected or printed. The workflow ran 40 Python tests,
JS client/layout checks, help synchronization and tracked-asset validation.
The downloaded archive contains 156 files, 15 teaching workflows and correct
0.1.0 metadata. Every file matched the published source commit. No model weights,
compiled/native binaries, caches or captures are included. Archive size: 308582
bytes; SHA256 `af4f4d63486929931fd66a3f2a58e350f68bd02c82ffaca2588f75bfbb8e7549`.

Registry reported `NodeVersionStatusPending` immediately after upload. This
confirms publication, not completed processing or Manager availability. Recheck
`https://api.comfy.org/nodes/genereticore/versions` before making that claim.
No broad clean Manager installation is claimed. See release-0.1.0.md for native
platform, helper-build and optional dependency requirements.

## Future publication

Update the semantic version and release notes, run the documented checks, commit
and push. Dispatch the manual **Publish to Comfy Registry** workflow on main.
Update the workflow's changelog filename and release-check version as necessary.
An ordinary push does not publish. Reusing an existing published version is not
a release update. Verify the uploaded archive and Registry processing status.
The repository secret is `REGISTRY_ACCESS_TOKEN`; manage it in GitHub settings,
never source, workflow JSON or chat. The publisher ID is the established Registry
identity and is independent of GitHub/HF account naming.
