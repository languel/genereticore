# Local API examples

This API is mounted in Comfy, restricted to loopback and same-origin browser requests. No native network listener starts.

```js
import { GeneretiCoreClient } from '/extensions/genereticore/js/client.js';
const client = new GeneretiCoreClient();
const { request_id } = await client.submit({
  task: 'text.generate', model: 'qwen3-0.6b',
  inputs: {prompt: 'Suggest a calm visual scene. /no_think'},
  options: {max_tokens: 128, temperature: 0},
  stream_id: 'my-scene', input_revision: 1, policy: 'latest'
});
await client.follow(request_id, event => {
  if (event.type === 'completed') {
    // Validate/consume the typed content in the creative application.
    console.log(event.payload.content);
  }
});
```

The extension URL follows the installed folder name. Use `POST /genereticore/tasks` with `task: 'model.download'` and a catalog model ID only when the user explicitly chooses to download. Ordinary inference never downloads.

Events have monotonically increasing `sequence`, `request_id`, `input_revision`, `timestamp`, `type`, and `payload`. Poll with `after` set to the last cursor. If `events_truncated` is true, prior partial events have expired; terminal complete content remains in the most recent event. Jobs expire after the bounded retention limit. Save required completed outputs in your creative application.

`latest` replaces pending work for its stream and suppresses an obsolete active result. It does not terminate an active model. Explicit cancellation terminates the helper; pending cancellation simply removes the job. `fifo` runs at most four pending jobs and rejects overload with HTTP 429. Download work should use FIFO.

Vision inputs use `image_base64` containing PNG/JPEG bytes, no data URL. Maximum encoded image data is 6 MB; native preprocessing bounds the longest edge to 1024. No remote image URL, local path, camera or screen capture is accepted. Decision inputs use `prompt` and `choices` (2–26 for the current Qwen adapter); their finite scores and labels are validated before delivery.

Current/next results are separate from model execution:

```js
import { ResultPair } from '/extensions/genereticore/js/client.js';
const images = new ResultPair();
images.accept(firstImage, 1);
images.accept(nextImage, 2, 'bar'); // previous output remains current
images.trigger('bar');           // call from your existing musical clock
images.setPhase(0.5);            // renderer consumes current, next and phase
images.setPhase(1);              // promote next to current
```

This primitive is tested without model inference; a real image-generation shader demo remains on the roadmap.
