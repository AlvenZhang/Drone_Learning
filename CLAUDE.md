# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a drone learning project (无人机学习项目) focused on teaching drone technology and programming. It includes both learning materials and simulation code for quadcopters (四旋翼无人机).

## Project Structure

```
├── docs/              # 学习资料 (Learning materials)
│   ├── basics/       # 基础知识
│   ├── advanced/     # 高级主题
│   └── projects/     # 项目案例
├── src/               # 源代码
│   ├── simulation/   # 仿真模块
│   ├── control/      # 控制算法
│   └── utils/        # 工具函数
├── examples/          # 示例代码
├── tests/           # 测试代码
└── data/            # 数据文件
```

## Common Commands

- Setup/Install dependencies: `uv sync`
- Run examples: `uv run python examples/01_hover_simulation.py`
- Add a new dependency: `uv add <package>`
- Run script in venv: `uv run <command>`

## Key Components

- `src/simulation/quadcopter.py`: Quadcopter dynamics model
- `src/simulation/simulator.py`: Simulation environment
- `src/control/pid.py`: PID controller implementation

## Learning Path

1. Read `docs/basics/` in order (01, 02, 03...
2. Run examples in `examples/`
