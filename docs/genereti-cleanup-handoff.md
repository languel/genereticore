# Genereti cleanup follow-up

GeneretiCore now supplies GeneretiCoreUpscale, a compact native Real-ESRGAN node and public verified model bundle. See esrgan.md and example 14. Keep learned native upscaling here; do not duplicate its backend in Genereti.

For the Genereti session: implement a lightweight RGB cleanup comparison using existing TOP/IMAGE/visual-view contracts. Start with explicit resize, mild spatial smoothing and optional edge antialiasing; compare against native Real-ESRGAN at equal output sizes. Add change-aware normalized temporal averaging separately from artistic top.feedback trails, with reset on scene change/source rewire/dimensions and a visible strength control. Previous-frame blending needs ghosting tests on moving edges. FSR1 is a potential later spatial upscaler; any vendored implementation must retain its own license/notices. RGB-only sources do not supply the depth, motion vectors or jitter required by FSR2/DLSS-style reconstruction.

Preserve explicit start, bounded queues, last-completed output, preview/overlay/backdrop shortcuts and compact accessible controls. Include processing/transport timings and actual delivered cadence; do not label reciprocal processing time as measured FPS.

Future segmentation and MediaPipe: browser-capable lightweight processing belongs in Genereti when browser runtime/model licensing and performance fit; substantial native inference belongs in GeneretiCore. Audit each model asset separately, retain provenance and public credits, and benchmark alongside live rendering. This is a direction, not an implemented segmentation milestone.
