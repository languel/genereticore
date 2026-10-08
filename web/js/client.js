/** Local explicit-start client. No capture, model execution or implicit downloads. */
export class GeneretiCoreClient {
  constructor(base = "/genereticore") { this.base = base; }
  async call(path, options) {
    const response = await fetch(this.base + path, options);
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }
  status() { return this.call("/status"); }
  submit(request) {
    return this.call("/tasks", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(request)});
  }
  cancel(id) { return this.call(`/tasks/${encodeURIComponent(id)}/cancel`, {method: "POST"}); }
  async follow(id, onEvent, {signal} = {}) {
    let cursor = 0;
    while (!signal?.aborted) {
      const result = await this.call(`/tasks/${encodeURIComponent(id)}?after=${cursor}`, {signal});
      for (const event of result.events) onEvent(event);
      cursor = result.cursor;
      if (["completed", "failed", "canceled", "superseded"].includes(result.state)) return result;
      await new Promise(resolve => setTimeout(resolve, 200));
    }
  }
}

/** Keep current output until a complete next frame arrives and its transition is triggered. */
export class ResultPair {
  constructor() { this.current = null; this.next = null; this.phase = 0; this.revision = -1; this.boundary = "immediate"; this.transitioning = false; }
  accept(result, revision, boundary = "immediate") {
    if (revision < this.revision) return false;
    if (!["immediate", "beat", "bar", "manual"].includes(boundary)) throw new Error("Unknown transition boundary");
    this.revision = revision;
    if (this.current === null) { this.current = result; return true; }
    this.next = result; this.phase = 0; this.boundary = boundary; this.transitioning = false;
    if (boundary === "immediate") this.trigger("immediate");
    return true;
  }
  trigger(boundary) {
    if (this.next === null || this.boundary !== boundary) return false;
    this.phase = 0; this.transitioning = true;
    return true; // Renderer drives setPhase using its own clock.
  }
  setPhase(value) {
    if (this.next === null || !this.transitioning) return;
    this.phase = Math.max(0, Math.min(1, value));
    if (this.phase === 1) { this.current = this.next; this.next = null; this.phase = 0; this.transitioning = false; }
  }
}
