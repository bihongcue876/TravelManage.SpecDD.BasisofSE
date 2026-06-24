"""
性能分析启动脚本 — profile 全量性能分析
用法：uv run python run_profiled.py                  （等待 Ctrl+C）
      uv run python run_profiled.py --timeout 30    （30 秒后自动停止）
"""
import argparse
import io
import os
import profile
import pstats
import threading
import time

import uvicorn

_server = None


def _auto_stop(delay: int):
    time.sleep(delay)
    if _server:
        print(f"\n[Profile] 超时 {delay} 秒，自动停止...")
        _server.should_exit = True


def run_profiled():
    global _server

    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=0, help="自动停止秒数")
    args = parser.parse_args()

    from main import app

    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    _server = uvicorn.Server(config)

    print("=" * 60)
    print("性能分析模式已启动（profile）")
    if args.timeout:
        print(f"将在 {args.timeout} 秒后自动停止")
        threading.Thread(target=_auto_stop, args=(args.timeout,), daemon=True).start()
    else:
        print("按 Ctrl+C 停止后输出分析结果")
    print("=" * 60)

    prof = profile.Profile()
    prof.runctx(
        "_server.run()",
        globals={"_server": _server},
        locals=None,
    )

    s = io.StringIO()
    pstats.Stats(prof, stream=s).sort_stats("cumtime").print_stats(30)
    result = s.getvalue()

    print("\n" + "=" * 60)
    print("性能分析结果 — 按累计耗时排序（前 30）")
    print("=" * 60)
    print(result)

    # 同时追加到 share/profiled_before.txt
    output_path = "share/profiled_before.txt"
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", output_path)
    full_path = os.path.normpath(full_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "a", encoding="utf-8") as f:
        f.write("\n\n=== 性能分析报告 " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===\n")
        f.write(result)
    print(f"\n结果已追加到 {output_path}")


if __name__ == "__main__":
    run_profiled()
