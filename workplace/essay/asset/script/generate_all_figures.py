"""从 workplace/output 的正式结果重新生成 essay/asset 全部论文图片。

本脚本只生成 PNG，不写表格、不调用 Q1–Q4 求解器。
运行：python essay/asset/script/generate_all_figures.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "output"
ASSET = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(ASSET / name, dpi=200, bbox_inches="tight")
    plt.close()


def nodes() -> dict[str, tuple[float, float]]:
    return {r["node_id"]: (float(r["longitude"]), float(r["latitude"]))
            for r in read_csv(OUTPUT / "final/nodes.csv")}


def plot_q1() -> None:
    rows = read_csv(OUTPUT / "q1/q1_payload_45.csv")
    services = sorted({r["service_id"] for r in rows})
    x = np.arange(len(services))
    plt.figure(figsize=(11, 4.5))
    for typ, marker in zip("ABC", ("o", "s", "^")):
        values = {r["service_id"]: float(r["safe_payload_kg"])
                  for r in rows if r["aircraft_type"] == typ}
        plt.plot(x, [values[s] for s in services], marker=marker, label=f"Type {typ}")
    plt.xticks(x, services, rotation=45)
    plt.ylabel("Safe payload (kg)")
    plt.legend(ncol=3)
    save("图6_1-1_Q1安全载荷.png")

    sensitivity = read_csv(OUTPUT / "q1/q1_sensitivity_global.csv")
    reserve = [100 * float(r["rho_A"]) for r in sensitivity]
    sorties = [int(r["total_sorties"]) for r in sensitivity]
    plt.figure(figsize=(6.2, 4.2))
    plt.plot(reserve, sorties, "o-", linewidth=2)
    plt.xticks(reserve)
    plt.xlabel("Return SOC reserve (%)")
    plt.ylabel("Minimum sorties")
    save("图6_1-2_返航余量敏感性.png")


def plot_routes(route_file: Path, name: str, relay_file: Path | None = None) -> None:
    xy = nodes()
    routes = read_csv(route_file)
    plt.figure(figsize=(8, 6.2))
    for route in routes:
        seq = ["O01"] + [x for x in route["service_sequence"].split(",") if x] + ["O01"]
        pts = [xy[x] for x in seq]
        plt.plot([p[0] for p in pts], [p[1] for p in pts], color="#7f8c8d", alpha=.28, linewidth=.8)
    plt.scatter([xy[k][0] for k in sorted(xy) if k != "O01"],
                [xy[k][1] for k in sorted(xy) if k != "O01"], s=35, color="#2878b5")
    for key, point in xy.items():
        plt.text(point[0], point[1], key, fontsize=7, ha="left", va="bottom")
    plt.scatter(*xy["O01"], marker="*", s=150, color="#c0392b", label="O01")
    if relay_file is not None:
        relay = read_csv(relay_file)
        plt.scatter([float(r["lon"]) for r in relay], [float(r["lat"]) for r in relay],
                    marker="^", s=70, color="#f39c12", label="Relay hover")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    save(name)


def gantt(rows, id_col, start_col, end_col, name, title) -> None:
    ids = sorted({r[id_col] for r in rows})
    y = {key: idx for idx, key in enumerate(ids)}
    plt.figure(figsize=(10, max(4, .38 * len(ids))))
    for r in rows:
        start, end = float(r[start_col]), float(r[end_col])
        plt.barh(y[r[id_col]], end - start, left=start, height=.62)
    plt.yticks(range(len(ids)), ids, fontsize=7)
    plt.xlabel("Time (s)")
    plt.title(title)
    save(name)


def plot_q2() -> None:
    plot_routes(OUTPUT / "q2/q2_routes.csv", "图6_2-1_Q2运输路线.png")
    gantt(read_csv(OUTPUT / "q2/q2_uav_timeline.csv"), "uav_id", "start_s", "return_s",
          "图6_2-2_运输无人机时序.png", "Transport UAV schedule")
    gantt(read_csv(OUTPUT / "q2/q2_battery_timeline.csv"), "battery_id", "occupation_start_s", "full_ready_s",
          "图6_2-3_电池周转时序.png", "Battery occupation through full charge")
    rows = [r for r in read_csv(OUTPUT / "q2/q2_box_delivery.csv") if r["expected_s"]]
    expected = [float(r["expected_s"]) for r in rows]
    delivered = [float(r["delivery_complete_s"]) for r in rows]
    high = max(expected + delivered)
    plt.figure(figsize=(6.2, 5.2))
    plt.scatter(expected, delivered, s=18, alpha=.7)
    plt.plot([0, high], [0, high], "r--", label="On-time boundary")
    plt.xlabel("Expected delivery time (s)")
    plt.ylabel("Actual delivery time (s)")
    plt.legend()
    save("图6_2-4_交付与期望时刻.png")


def plot_q3() -> None:
    plot_routes(OUTPUT / "q3/q3_transport_routes.csv", "图6_3-1_Q3运输与中继位置.png",
                OUTPUT / "q3/q3_relay_sorties.csv")
    intervals = read_csv(OUTPUT / "q3/q3_communication_intervals.csv")
    ids = sorted({r["transport_sortie_id"] for r in intervals})
    y = {key: idx for idx, key in enumerate(ids)}
    colors = {"DIRECT": "#2878b5", "RELAY": "#f39c12"}
    plt.figure(figsize=(11, 7))
    labels = set()
    for r in intervals:
        mode = r["mode"]
        label = mode if mode not in labels else None
        labels.add(mode)
        plt.barh(y[r["transport_sortie_id"]], float(r["end_s"]) - float(r["start_s"]),
                 left=float(r["start_s"]), height=.68, color=colors.get(mode, "#777777"), label=label)
    plt.yticks(range(len(ids)), ids, fontsize=6)
    plt.xlabel("Time (s)")
    plt.legend()
    save("图6_3-2_通信保障时间线.png")

    margins = read_csv(OUTPUT / "q3/q3_link_margin.csv")
    plt.figure(figsize=(10, 4.3))
    plt.scatter([float(r["start_s"]) for r in margins],
                [float(r["margin_lower_bound_db"]) for r in margins], s=12, alpha=.75)
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Interval start time (s)")
    plt.ylabel("Certified margin lower bound (dB)")
    save("图6_3-3_连续认证链路余量.png")

    samples = read_csv(OUTPUT / "q3/q3_sampling_convergence.csv")
    plt.figure(figsize=(6.3, 4.2))
    plt.plot([float(r["spacing_m"]) for r in samples],
             [float(r["minimum_sampled_margin_db"]) for r in samples], "o-")
    plt.gca().invert_xaxis()
    plt.xlabel("Trajectory sampling spacing (m)")
    plt.ylabel("Minimum sampled margin (dB)")
    save("图6_3-4_通信采样收敛.png")

    relay = [r for r in intervals if r["mode"] == "RELAY"]
    counts = {}
    durations = {}
    for r in relay:
        key = r["transport_sortie_id"]
        counts[key] = counts.get(key, 0) + 1
        durations[key] = durations.get(key, 0.0) + float(r["end_s"]) - float(r["start_s"])
    keys = sorted(counts)
    plt.figure(figsize=(10, 4.3))
    plt.bar(keys, [durations[k] for k in keys])
    plt.xticks(rotation=60, fontsize=7)
    plt.ylabel("Relay-required duration (s)")
    save("图6_3-7_Q3直连盲区.png")

    transport = read_csv(OUTPUT / "q3/q3_transport_routes.csv")
    relay_tasks = read_csv(OUTPUT / "q3/q3_relay_sorties.csv")
    joined = ([{"id": r["sortie_id"], "start": r["start_s"], "end": r["return_s"], "kind": "transport"}
               for r in transport] +
              [{"id": r["sortie_id"], "start": r["start_s"], "end": r["return_s"], "kind": "relay"}
               for r in relay_tasks])
    y = {r["id"]: i for i, r in enumerate(joined)}
    plt.figure(figsize=(11, 8))
    for r in joined:
        plt.barh(y[r["id"]], float(r["end"]) - float(r["start"]), left=float(r["start"]),
                 color="#2878b5" if r["kind"] == "transport" else "#f39c12", height=.65)
    plt.yticks(range(len(joined)), [r["id"] for r in joined], fontsize=6)
    plt.xlabel("Time (s)")
    save("图6_3-8_Q3联合时序.png")


def plot_q4() -> None:
    xy = nodes()
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.3), constrained_layout=True)
    for axis, k in zip(axes, (2, 3)):
        rows = read_csv(OUTPUT / f"q4/q4_k{k}_partition.csv")
        palette = ("#2878b5", "#f39c12", "#2ca02c")
        for r in rows:
            services = [x for x in r["services"].split(",") if x]
            group = int(r["group"])
            axis.scatter([xy[s][0] for s in services], [xy[s][1] for s in services],
                         s=45, color=palette[group - 1], label=f"Group {group}")
            for s in services:
                axis.text(xy[s][0], xy[s][1], s, fontsize=7, ha="left", va="bottom")
        axis.set_title(f"K={k}")
        axis.set_xlabel("Longitude")
        axis.set_ylabel("Latitude")
        axis.legend()
    fig.savefig(ASSET / "图6_3-5_Q4两组与三组分区.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    gap = read_csv(OUTPUT / "q4/q4_resource_gap.csv")
    resources = sorted({r["resource_type"] for r in gap})
    k2 = {r["resource_type"]: r for r in gap if r["K"] == "2"}
    k3 = {r["resource_type"]: r for r in gap if r["K"] == "3"}
    x = np.arange(len(resources)); width = .25
    plt.figure(figsize=(11, 4.7))
    plt.bar(x - width, [float(k2[r]["inventory"]) for r in resources], width, label="Inventory")
    plt.bar(x, [float(k2[r]["split_requirement"]) for r in resources], width, label="K=2")
    plt.bar(x + width, [float(k3[r]["split_requirement"]) for r in resources], width, label="K=3")
    plt.xticks(x, resources, rotation=35, ha="right")
    plt.ylabel("Independent resource requirement")
    plt.legend(ncol=3)
    save("图6_3-6_Q4资源需求与库存.png")

    plt.figure(figsize=(11, 4.7))
    plt.bar(x - .18, [float(k2[r]["gap"]) for r in resources], .18, label="K=2 gap")
    plt.bar(x, [float(k3[r]["gap"]) for r in resources], .18, label="K=3 gap")
    plt.bar(x + .18, [float(k3[r]["redundancy"]) for r in resources], .18, label="K=3 redundancy")
    plt.xticks(x, resources, rotation=35, ha="right")
    plt.legend(ncol=3)
    save("图6_3-9_Q4缺口与冗余.png")

    plt.figure(figsize=(7, 4.5))
    for k, marker in ((2, "o"), (3, "s")):
        rows = read_csv(OUTPUT / f"q4/q4_k{k}_partition.csv")
        plt.plot([int(r["group"]) for r in rows], [float(r["workload_resource_s"]) for r in rows],
                 marker=marker, linewidth=2, label=f"K={k}")
    plt.xlabel("Group")
    plt.ylabel("Workload (resource-s)")
    plt.legend()
    save("图6_3-10_Q4工作量平衡.png")


def main() -> None:
    required = [OUTPUT / "q1/q1_results.xlsx", OUTPUT / "q2/q2_results.xlsx",
                OUTPUT / "q3/q3_results.xlsx", OUTPUT / "q4/q4_results.xlsx"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("缺少正式结果：" + ", ".join(missing))
    plot_q1()
    plot_q2()
    plot_q3()
    plot_q4()
    print("FIGURES_GENERATED = 16")


if __name__ == "__main__":
    main()
