import { app } from "../../../scripts/app.js";
import { GeneretiCoreClient } from "./client.js";
import { resultViewer } from "./result-viewer.js";
import {arrange} from "./layout.js";
const client = new GeneretiCoreClient();
const taskTypes = {GeneretiCoreText: "text.generate", GeneretiCoreVision: "vision.analyze", GeneretiCoreDecision: "decision.evaluate"};

function button(glyph, title, action) {
  const b = document.createElement("button");
  b.type="button"; b.textContent = glyph; b.title = title; b.setAttribute("aria-label", title);
  Object.assign(b.style, {border: "none", background: "transparent", color: "inherit", display:"inline-flex", alignItems:"center", justifyContent:"center", padding:"0", width: "20px", height: "20px", fontSize: "12px", borderRadius: "6px", cursor: "pointer"});
  b.addEventListener("click", action);
  return b;
}
app.registerExtension({
  name: "GeneretiCore.LocalTasks",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const task = taskTypes[nodeData.name];
    const core = nodeData.name.startsWith("GeneretiCore");
    const companionLabels = {GeneretiLivecode:"ꘇ livecode", GeneretiLiveImagePreview:"ꘇ image preview", GeneretiDatLesson:"ꘇ lesson"};
    if (!core && !companionLabels[nodeData.name]) return;
    const compactTitle = node => {
      const label = core ? nodeData.display_name : companionLabels[nodeData.name];
      if (core && /^[ꘇꘅ]/.test(node.title ?? "")) node.title = "ꘅ " + node.title.replace(/^(?:[ꘇꘅ]\s*)+/, "");
      else if (companionLabels[nodeData.name] && /^(?:ꘇ )?Genereti/.test(node.title ?? ""))
        node.title = companionLabels[nodeData.name] + (node.title.includes(" · ") ? " · " + node.title.split(" · ").slice(1).join(" · ") : "");
      else if (core && node.title === nodeData.name && label) node.title = label;
    };
    const configure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function(){const result=configure?.apply(this,arguments);compactTitle(this);return result;};
    if (!core) return;
    const original = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
      const result = original?.apply(this, arguments);
      const node = this;
      node.properties.node_type = nodeData.name;
      if (nodeData.name === "GeneretiCoreTutorial") {
        const book = button("▤", "Open Tutorial 0: decision models and creative controls", () => window.open(new URL("../tutorial-0.html", import.meta.url).href, "_blank"));
        const tutorial=node.addDOMWidget("tutorial", "tutorial", book, {serialize:false});
        tutorial.options.getMinHeight=()=>34; tutorial.options.getMaxHeight=()=>34;
      }
      if (!task && !["GeneretiCoreResult", "GeneretiCoreValidateDecision"].includes(nodeData.name)) return result;
      const output = resultViewer(node);
      const showResult = text => output.show(text);
      node._genereticoreShowResult = showResult;
      const executed = node.onExecuted;
      node.onExecuted = function(message) {
        executed?.apply(this, arguments);
        if (Array.isArray(message?.text)) showResult(message.text.join("\n"));
        const validation = message?.validation?.[0];
        if (validation?.valid === false) {
          // Clear our own downstream viewers so an earlier answer cannot look current.
          const graph = node.graph ?? app.graph;
          const visited = new Set([node.id]), pending = [node];
          while (pending.length) {
            const current = pending.pop();
            for (const socket of current.outputs ?? []) for (const id of socket.links ?? []) {
              const link = graph.links[id];
              const target = link && graph.getNodeById(link.target_id);
              if (!target || visited.has(target.id)) continue;
              visited.add(target.id); pending.push(target);
              if (target.type === "GeneretiCoreResult") target._genereticoreShowResult?.(
                "Not updated: upstream decision needs correction.\n" + validation.message);
            }
          }
        }
      };
      let outputWidget;
      const addOutput = () => {
        const viewer = node.addDOMWidget("genereticore_result", "genereticore_result", output.element, {serialize: false, hideOnZoom: false});
        outputWidget=viewer;
        node._generetiPreviewFirstWidget=viewer;
        viewer.computeSize = () => [node.size[0], 210];
        viewer.options.getMinHeight = () => 210;
        viewer.options.getMaxHeight = () => 210;
      };
      if (!task) { addOutput(); arrange(node,[outputWidget]); return result; }
      const streamID = `node-${crypto.randomUUID()}`;
      const bar = document.createElement("div");
      bar.className = "genereticore-controls";
      Object.assign(bar.style, {display: "flex", alignItems: "center", gap: "0", color: "var(--input-text, currentColor)", font: "12px sans-serif", minHeight: "20px"});
      const status = document.createElement("span");
      status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
      status.textContent = "local · idle";
      const value = name => node.widgets?.find(w => w.name === name)?.value;
      let requestID = null, revision = 0, removed = false, inFlight = false;
      let lastCompleted = null;
      const run = async download => {
        if (inFlight) return;
        inFlight = true;
        try {
          const inputs = download ? {} : {prompt: value("prompt")};
          if (!download && task === "decision.evaluate") { inputs.choices = JSON.parse(value("choices_json")); inputs.question = value("question") ?? "Which option best fits the situation?"; }
          if (!download && task === "vision.analyze") throw new Error("Use Comfy Run for connected IMAGE input. Live clients may submit image_base64 explicitly.");
          const currentRevision = ++revision;
          const submitted = await client.submit({task: download ? "model.download" : task, model: value("model"), inputs,
            options: {max_tokens: value("max_tokens"), temperature: value("temperature") ?? 0},
            policy: download ? "fifo" : "latest", stream_id: streamID, input_revision: currentRevision});
          requestID = submitted.request_id;
          if (removed) { await client.cancel(requestID); return; }
          status.textContent = download ? "downloading…" : "queued…";
          await client.follow(requestID, event => {
            if (removed || event.input_revision !== revision) return;
            if (event.type === "download_progress") status.textContent = `↓ ${Math.round(event.payload.fraction * 100)}%`;
            else if (event.type === "completed") {
              lastCompleted = event.payload;
              status.textContent = download ? "installed" : `preview · ${Math.round(event.payload.timings?.total_ms ?? 0)} ms`;
              status.title = download ? "Model installed. Use Run for connected outputs." : "Local preview only. Use Run to update connected nodes.";
              if (!download) showResult(lastCompleted.content.text ?? JSON.stringify(lastCompleted.content));
              window.dispatchEvent(new CustomEvent("genereticore:completed", {detail: {node_id: node.id, ...event}}));
            } else if (event.type === "failed") status.textContent = event.payload.message;
            else if (event.type === "verify_progress") status.textContent = `checking · ${Math.round(event.payload.fraction * 100)}%`;
            else if (["loading", "load_progress"].includes(event.type)) status.textContent = "loading…";
            else if (event.type === "started") status.textContent = "running…";
            else if (event.type === "canceled") status.textContent = "canceled";
            else if (event.type === "superseded") status.textContent = "replaced";
            else if (event.type === "queued") status.textContent = "queued…";
          });
        } catch (error) { if (!removed) status.textContent = error.message; }
        finally { requestID = null; inFlight = false; }
      };
      bar.append(button("↓", "Download this pinned model from Hugging Face into Comfy's model folder", () => run(true)),
        button("▷", "Run the current workflow and update connected result nodes", async () => {
          try { status.textContent = "queued workflow…"; await app.queuePrompt(0, 1); }
          catch (error) { status.textContent = error.message; }
        }),
        ...(task === "vision.analyze" ? [] : [button("ϟ", "Local preview here only; connected nodes update with Run", () => run(false))]),
        button("□", "Cancel the active task and release the native helper", async () => {
          if (requestID) { try { await client.cancel(requestID); } catch (e) { status.textContent = e.message; } }
        }), status);
      const widget = node.addDOMWidget("genereticore", "genereticore", bar, {serialize: false, hideOnZoom: false});
      widget.computeSize = () => [node.size[0], 24];
      widget.options.getMinHeight = () => 24;
      widget.options.getMaxHeight = () => 24;
      addOutput();
      arrange(node,[widget,outputWidget]);
      const priorExecuted = node.onExecuted;
      node.onExecuted = function(message) { priorExecuted?.apply(this, arguments); status.textContent = "workflow complete"; };
      const onRemoved = node.onRemoved;
      node.onRemoved = function() { removed = true; if (requestID) client.cancel(requestID).catch(() => {}); return onRemoved?.apply(this, arguments); };
      return result;
    };
  },
  setup() {
    const style = document.createElement("style");
    style.textContent = `.genereticore-result{height:100%;min-height:0;display:flex;flex-direction:column;color:var(--input-text,currentColor);background:transparent;border-radius:0;font:12px/1.5 monospace}.genereticore-result-body{overflow:auto;flex:1;padding:8px;min-height:0;user-select:text}.genereticore-result textarea{width:100%;height:100%;min-height:145px;box-sizing:border-box;border:0;resize:none;background:transparent;color:inherit;font:inherit}.genereticore-controls select{border:0;background:transparent;color:inherit;height:20px;border-radius:6px}.genereticore-children{padding-left:14px;border-left:1px solid color-mix(in srgb,currentColor 15%,transparent)}.genereticore-result summary{cursor:pointer}.genereticore-key{opacity:.8}.genereticore-string{color:var(--p-green-400,#9acfa3)}.genereticore-number{color:var(--p-blue-400,#97b7dc)}.genereticore-boolean,.genereticore-null{color:var(--p-purple-400,#c1a6d8)}.genereticore-controls button:hover {background:color-mix(in srgb,currentColor 10%,transparent)!important} .genereticore-controls button[aria-pressed=true]{background:color-mix(in srgb,currentColor 12%,transparent)!important}.genereticore-controls button:focus-visible{outline:2px solid currentColor;outline-offset:-2px}.genereticore-controls span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}`;
    style.textContent += `
    .genereticore-controls select{font:inherit;height:20px;border:0;box-shadow:none;padding:0 7px;color:var(--input-text,currentColor)}
    .genereticore-controls select:hover{background:color-mix(in srgb,currentColor 10%,transparent)}
    .genereticore-controls select:focus-visible{outline:2px solid currentColor;outline-offset:-2px}
    @supports(appearance:base-select){
      .genereticore-glyph-choice,.genereticore-glyph-choice::picker(select){appearance:base-select}
      .genereticore-glyph-choice{width:20px;min-width:20px;padding:0 2px;font-size:0!important;gap:0}
      .genereticore-glyph-choice::picker(select),.genereticore-glyph-choice option{font-size:12px}
      .genereticore-glyph-choice::picker-icon,.genereticore-glyph-choice option::checkmark{display:none}
      .genereticore-glyph-choice>button{display:contents}
      .genereticore-glyph-choice selectedcontent{display:flex;align-items:center;justify-content:center}
      .genereticore-glyph-choice selectedcontent .genereticore-choice-label{display:none}
      .genereticore-choice-icon{display:inline-flex;align-items:center}
      .genereticore-glyph-choice::picker-icon{margin-left:0}
      .genereticore-glyph-choice::picker(select){min-width:160px;padding:4px;color:var(--input-text,currentColor);background:var(--comfy-input-bg,#222);border:1px solid var(--border-color,#555);border-radius:6px;font:inherit}
      .genereticore-glyph-choice option{display:flex;align-items:center;gap:8px;min-height:20px;padding:0 8px;border-radius:6px}
      .genereticore-glyph-choice option:hover,.genereticore-glyph-choice option:checked{background:color-mix(in srgb,currentColor 10%,transparent)}
    }`;
    document.head.append(style);
  }
});
