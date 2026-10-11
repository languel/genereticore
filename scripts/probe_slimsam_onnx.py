"""Local CPU contract probe for the two-file SlimSAM ONNX export.

Contributor-only: requires numpy and onnxruntime. No downloads or media uploads.
Synthetic input establishes execution/shape/finite output, not segmentation quality,
browser compatibility, tracking or end-to-end live performance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import time


def main():
    import numpy as np
    import onnxruntime as ort
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--encoder', type=Path, required=True)
    parser.add_argument('--decoder', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--iterations', type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 20:
        parser.error('iterations must be between 1 and 20')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    start = time.perf_counter()
    encoder = ort.InferenceSession(str(args.encoder), options, providers=['CPUExecutionProvider'])
    decoder = ort.InferenceSession(str(args.decoder), options, providers=['CPUExecutionProvider'])
    load_ms = (time.perf_counter() - start) * 1000
    # One synthetic square image, ImageNet-normalized as the pinned processor requires.
    image = np.zeros((1, 3, 1024, 1024), dtype=np.float32)
    image[:, :, 256:768, 256:768] = 1
    mean = np.array([.485, .456, .406], dtype=np.float32).reshape(1, 3, 1, 1)
    std = np.array([.229, .224, .225], dtype=np.float32).reshape(1, 3, 1, 1)
    image = (image - mean) / std
    def encode():
        return dict(zip([o.name for o in encoder.get_outputs()], encoder.run(None, {'pixel_values': image})))
    def decode(embeddings):
        inputs = {**embeddings, 'input_points': np.array([[[[512, 512]]]], dtype=np.float32),
                  'input_labels': np.array([[[1]]], dtype=np.int64)}
        return dict(zip([o.name for o in decoder.get_outputs()], decoder.run(None, inputs)))
    start = time.perf_counter()
    embeddings = encode()
    outputs = decode(embeddings)
    first_run_ms = (time.perf_counter() - start) * 1000
    assert all(np.isfinite(v).all() for v in outputs.values())
    assert outputs['pred_masks'].shape == (1, 1, 3, 256, 256)
    encoder_ms, decoder_ms = [], []
    for _ in range(args.iterations):
        start = time.perf_counter(); embeddings = encode()
        encoder_ms.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter(); outputs = decode(embeddings)
        decoder_ms.append((time.perf_counter() - start) * 1000)
    report = {'scope': 'synthetic local CPU contract probe; no quality or browser benchmark',
              'machine': platform.machine(), 'os': platform.mac_ver()[0], 'onnxruntime': ort.__version__,
              'providers': encoder.get_providers(), 'intra_op_threads': 2,
              'artifacts': [{'name': p.name, 'bytes': p.stat().st_size,
                             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in [args.encoder, args.decoder]],
              'load_ms': round(load_ms, 2), 'first_encoder_and_decoder_ms': round(first_run_ms, 2),
              'warm_encoder_ms': [round(t, 2) for t in encoder_ms],
              'warm_decoder_ms': [round(t, 2) for t in decoder_ms],
              'output_shapes': {k: list(v.shape) for k, v in outputs.items()}, 'finite_outputs': True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
