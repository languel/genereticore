# Image bundle credits and redistribution review

Reviewed October 10, 2026 for public converted evaluation bundles. This records
published upstream terms and the notices shipped; it does not relicense any source.
Every download retains Notice.txt and full license copies in the local model root
under licenses/<family>/<revision>. The node's ⓘ link opens credits and terms.

| Component | Upstream | Published terms | Distribution |
| --- | --- | --- | --- |
| SDXS DreamShaper base and Sketch | [IDKiro base](https://huggingface.co/IDKiro/sdxs-512-dreamshaper), [Sketch](https://huggingface.co/IDKiro/sdxs-512-dreamshaper-sketch) | Cards explicitly declare OpenRAIL++ | Converted packages public; retain use restrictions, credits and change notices |
| DreamShaper teacher lineage | [Lykon DreamShaper 8](https://huggingface.co/Lykon/dreamshaper-8), [LCM](https://huggingface.co/Lykon/dreamshaper-8-lcm) | CreativeML OpenRAIL-M | Preserve these terms alongside SDXS's declaration |
| SD Turbo | [Stability AI](https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/LICENSE.md) | Stability AI Community License, July 5, 2024 | Public converted package with full agreement, required Notice and Powered by Stability AI attribution |
| Tiny VAE encoder/decoder | [TAESD, Ollin Boer Bohan](https://github.com/madebyollin/taesd) via SDXS Tiny VAE | MIT | Include copyright and permission notice |
| Text encoder implementations | [OpenAI CLIP](https://github.com/openai/CLIP), [OpenCLIP contributors](https://github.com/mlfoundations/open_clip) | MIT | Retain implementation notices; weights also retain source package terms |
| Optional Canny ControlNet | [thibaud/controlnet-sd21-canny-diffusers](https://huggingface.co/thibaud/controlnet-sd21-canny-diffusers) | Card says other and refers to different preprocessors | Do not mirror; see original source or use supported SDXS sketch/Turbo image instead |

Both RAIL texts permit redistribution subject to their conditions, including
passing on the use restrictions and identifying changes. SDXS provides a license
tag rather than a full license file. The included OpenRAIL++ reference text comes
from the official Stability AI SDXL repository, explicitly identified as a reference
copy in Notice.txt; it is not represented as a file supplied by IDKiro. The original
SDXS and Sketch model cards are retained unchanged. The teacher's OpenRAIL-M
reference text is from CompVis's official license Space. Exact source URLs and
revisions for every license copy are in licenses/image/sources.json.

Turbo's agreement permits research/non-commercial distribution subject to its
conditions. Commercial use has registration/revenue conditions; the student and
publisher must follow the actual agreement for their own use. We have not registered
anyone for commercial use or accepted a separate enterprise agreement. These model
terms are distinct from GeneretiCore's MIT code license. No licensing conclusion is
made about datasets that were used upstream.

The modified weights use fixed 512px tensors, FP16 Core ML conversion, and a fused
SDXS sketch controller/denoiser. Notice.txt identifies every .mlpackage as modified;
there is no claim of original authorship of the underlying model. Provenance contains
pinned model revisions and conversion versions. Neither user media nor credentials
are part of the published repositories. Public access does not imply unrestricted
use or hosted inference.

## Optional Canny from the original source

The public bundles work without Canny. SDXS sketch is the supplied outline-guided
alternative; Turbo image is the supplied remix alternative. Do not replace Canny
with an SD 1.5/SDXL ControlNet: the current Turbo engine expects SD 2.1 residual shapes.

Contributors who independently establish appropriate permission can download the
original Canny source at revision `9c3106f9154d708550f2c83d231fbd648da7b670`, then
use the public archived conversion recipe:
[convert_controls.py](https://github.com/languel/genereti/blob/main/integrations/legacy-generator/scripts/convert_controls.py).
In a separate conversion environment (Python 3.11, coremltools 8.3, Torch 2.5.1,
Diffusers 0.32.2), cache the pinned SD Turbo fp16 UNet and run
`python scripts/convert_controls.py --size 512 --guides canny` from that archive.
The recipe writes `models/512/control_canny.mlpackage` and
`models/512/turbo_residual_unet.mlpackage`. Add both to your configured image model
root's 512 directory, refresh Comfy, choose Canny, and enable preprocessing for raw
images. These are contributor instructions, not an approved student mirror or a
claim that the upstream license permits every use. No third-party author was
contacted or agreement accepted on the user's behalf.
