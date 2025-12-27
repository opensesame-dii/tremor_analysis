#!/usr/bin/env python3
import argparse
import csv
import math
import random
from typing import List

# ---- Constants ----
DATA_ROWS = 1000
SAMPLE_INTERVAL = 1.0

FREQ_RANGE_HZ = (0.02, 0.06)
AMPLITUDE_RANGE = (0.1, 2.0)
PHASE_RANGE_RAD = (0.0, 2.0 * math.pi)

NOISE_VARIANCE = 0.03

HEADER_ROWS = [
    [
        "this",
        "is",
        "sample",
        "file",
        "with",
        "shift-jis",
        "（日本語）",
        "text",
        "encoding",
        "",
    ],
    [
        "this",
        "area",
        "may",
        "contain",
        "settings",
        "written",
        "by",
        "measurement",
        "system",
        "",
    ],
    ["for", "example", ""],
    ["product name", "motion sensor", ""],
    ["id", "1", ""],
    ["comment", ""],
    ["sampling_rate", "200", ""],
    ["key:0123456789abcdef", ""],
    ["time:12:34:56", ""],
    [
        "index",
        "sensor_1_x",
        "sensor_1_y",
        "sensor_1_z",
        "sensor_2_x",
        "sensor_2_y",
        "sensor_2_z",
        "sensor_3_x",
        "sensor_3_y",
        "sensor_3_z",
        "",
    ],
]
DIMENSIONS = 3
GROUPS = 3


def _random_params() -> tuple[float, float, float]:
    freq = random.uniform(*FREQ_RANGE_HZ)
    amp = random.uniform(*AMPLITUDE_RANGE)
    phase = random.uniform(*PHASE_RANGE_RAD)
    return freq, amp, phase


def _generate_group(freq: float, amp: float, phase: float, t: float) -> List[float]:
    # 3D sine wave values with independent Gaussian noise per axis.
    values = []
    for axis_shift in (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0):
        base = amp * math.sin(2.0 * math.pi * freq * t + phase + axis_shift)
        noise = random.gauss(0.0, math.sqrt(NOISE_VARIANCE))
        values.append(base + noise)
    return values


def generate_rows() -> List[List[float]]:
    group_params = [_random_params() for _ in range(GROUPS)]
    rows: List[List[float]] = []
    for i in range(DATA_ROWS):
        t = i * SAMPLE_INTERVAL
        row: List[float] = []
        for freq, amp, phase in group_params:
            row.extend(_generate_group(freq, amp, phase, t))
        rows.append(row)
    return rows


def write_csv(path: str) -> None:
    rows = generate_rows()
    with open(path, "w", newline="", encoding="shift_jis") as f:
        writer = csv.writer(f)
        for row in HEADER_ROWS:
            writer.writerow(row)
        for idx, row in enumerate(rows, start=1):
            writer.writerow([idx] + row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample tremor CSV.")
    parser.add_argument("output_csv", help="Output CSV filename")
    args = parser.parse_args()
    write_csv(args.output_csv)


if __name__ == "__main__":
    main()
