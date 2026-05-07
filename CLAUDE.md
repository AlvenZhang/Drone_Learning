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
│   └── control/      # 控制算法
├── examples/          # 示例代码
└── data/              # 数据文件
```

## Common Commands

- Setup/Install dependencies: `uv sync`
- Run examples: `uv run python examples/01_hover_simulation.py`
- Add a new dependency: `uv add <package>`
- Run script in venv: `uv run <command>`
- Run main entry: `uv run python main.py`

## Key Components

- `src/simulation/quadcopter.py`: Quadcopter dynamics model using ENU coordinate system (东-北-上)
- `src/simulation/simulator.py`: Simulation environment that runs the simulation and records state history
- `src/control/pid.py`: PID controller implementation with output limiting

## Learning Path

1. Read `docs/basics/` in order (01-introduction.md, 02-quadcopter.md, 03-coordinate-systems.md...)
2. Run examples in `examples/`

## Architecture Notes

- **Quadcopter Dynamics**: The `Quadcopter` class implements a 12-state dynamic model (position, velocity, attitude, angular rates) using Euler integration. It uses an X-shaped motor configuration with motor mixing logic to convert thrust/torque commands to individual motor speeds.

- **Simulation**: The `Simulator` class handles running the simulation loop, recording state history, and providing trajectory data for analysis. Controllers can be passed as callback functions to the `run()` method.

- **Control**: The `PIDController` class provides basic PID control with integral windup protection via output limits. Controllers in examples take a `Quadcopter` instance and time `t` as inputs, returning motor speeds squared.

- **Coordinate System**: ENU (East-North-Up) is used throughout, with z=0 as the ground plane.

