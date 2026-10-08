import argparse
from dataclasses import asdict
import json
from pathlib import Path
from .coreml import LocalBackend
from .contracts import Request
from .runtime import TaskRuntime


def main():
    parser = argparse.ArgumentParser(description="Local GeneretiCore tasks")
    parser.add_argument("command", choices=["doctor", "download", "text", "decision", "vision"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--model-dir")
    parser.add_argument("--helper")
    parser.add_argument("--prompt", default="What is the capital of Japan? /no_think")
    parser.add_argument("--choices", default='["blue", "orange"]')
    parser.add_argument("--image")
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    backend = LocalBackend(args.model_dir, args.helper)
    if args.command == "doctor":
        print(json.dumps({"capability": asdict(backend.capability()), "models": backend.catalog()}, indent=2))
        return
    task = {"download": "model.download", "text": "text.generate", "decision": "decision.evaluate", "vision": "vision.analyze"}[args.command]
    inputs = {"prompt": args.prompt}
    if args.command == "decision":
        inputs["choices"] = json.loads(args.choices)
    if args.command == "vision":
        import base64
        if not args.image:
            parser.error("vision requires --image")
        inputs["image_base64"] = base64.b64encode(Path(args.image).read_bytes()).decode()
    runtime = TaskRuntime(backend)
    try:
        for _ in range(args.repeat):
            job = runtime.submit(Request(task, args.model or ("qwen3-vl-2b" if args.command == "vision" else "qwen3-0.6b"), inputs, {"max_tokens": args.max_tokens}))
            print(json.dumps(job.future.result(timeout=600), indent=2))
    finally:
        runtime.close()

if __name__ == "__main__":
    main()
