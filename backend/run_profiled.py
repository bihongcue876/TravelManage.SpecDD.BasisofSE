"""
性能分析启动脚本 — profile 全量性能分析
用法：uv run python run_profiled.py
按 Ctrl+C 停止后，终端打印各函数累计耗时排名
"""
import io
import profile
import pstats
import sys

import uvicorn


def run_profiled():
    from main import app

    prof = profile.Profile()

    print("=" * 60)
    print("性能分析模式已启动（profile）")
    print("按 Ctrl+C 停止后输出分析结果")
    print("=" * 60)

    try:
        prof.runctx(
            "uvicorn.run(app, host='0.0.0.0', port=8000)",
            globals={"uvicorn": uvicorn, "app": app},
            locals=None,
        )
    except KeyboardInterrupt:
        pass

    s = io.StringIO()
    pstats.Stats(prof, stream=s).sort_stats("cumtime").print_stats(30)
    print("\n" + "=" * 60)
    print("性能分析结果 — 按累计耗时排序（前 30）")
    print("=" * 60)
    print(s.getvalue())


if __name__ == "__main__":
    run_profiled()
