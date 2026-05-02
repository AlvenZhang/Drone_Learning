# 开源飞控大集合！

飞控开源项目非常多，这是最好的学习资源！

---

## 目录
1. [穿越机类飞控](#穿越机类飞控-速度与激情)
2. [专业类飞控](#专业类飞控-功能全)
3. [学习类飞控](#学习类飞控-专门给新手的)
4. [怎么学](#怎么学这些开源代码)

---

## 穿越机类飞控 (速度与激情)

### 1. BetaFlight ⭐⭐⭐⭐⭐ 最推荐！

#### 简介
- 现在最火的开源飞控固件
- 专门为穿越机设计
- 代码质量高，社区活跃
- 支持的飞控板超多！

#### 支持的硬件
- F3, F4, F7, H7 系列STM32
- 市面上绝大多数飞控都支持

#### 特点
- 调参软件简洁好用 (BetaFlight Configurator)
- PID调参很方便
- 支持黑盒子记录飞行数据
- 支持OSD (屏幕显示飞行数据)

#### 去哪里找
- GitHub: https://github.com/betaflight/betaflight
- 官网: https://betaflight.com

#### 学习难度
- ⭐⭐⭐ 稍有点复杂，但社区资料多

---

### 2. CleanFlight

#### 简介
- BetaFlight的前身
- 老一点，但是代码结构简单一点
- 适合学习基础

#### GitHub
- https://github.com/cleanflight/cleanflight

---

### 3. INAV

#### 简介
- 从CleanFlight分出来的
- 侧重GPS导航、定点飞行
- 适合做航拍、测绘

#### GitHub
- https://github.com/iNavFlight/inav

---

## 专业类飞控 (功能全)

### 1. PX4 ⭐⭐⭐⭐⭐ 超级强大！

#### 简介
- 无人机开源固件的"老大哥"
- 功能超级全！
- 从四轴到固定翼、垂直起降都支持
- 很多商业无人机都用这个

#### 特点
- 支持多种机型
- 自动驾驶功能强
- 支持计算机视觉 (ROS)
- 代码结构非常规范，适合学习

#### 支持的硬件
- Pixhawk (1/2/4/6x系列)
- Pixracer
- 还有好多好多...

#### 去哪里找
- GitHub: https://github.com/PX4/PX4-Autopilot
- 官网: https://px4.io
- 文档: https://docs.px4.io (超级详细！)

#### 学习难度
- ⭐⭐⭐⭐⭐ 有点复杂，但是资料超级全

---

### 2. ArduPilot (APM) ⭐⭐⭐⭐⭐

#### 简介
- 另一个巨头！
- 跟PX4齐名
- 历史悠久，用户基数大
- 功能同样强大

#### 特点
- 支持多平台 (Windows/Mac/Linux)
- 地面站软件Mission Planner超级好用
- 支持各种机型

#### 支持的硬件
- Pixhawk系列
- 还有很多...

#### 去哪里找
- GitHub: https://github.com/ArduPilot/ardupilot
- 官网: https://ardupilot.org

#### 学习难度
- ⭐⭐⭐⭐ 跟PX4差不多

---

## 学习类飞控 (专门给新手的)

### 1. MultiWii ⭐⭐⭐⭐ 入门首选！

#### 简介
- 曾经的王者！
- 代码结构简单！
- 特别适合初学者读
- 支持Arduino！

#### 特点
- 可以在Arduino上跑！
- 代码量不算大
- 容易看懂

#### GitHub
- https://github.com/multiwii

#### 学习难度
- ⭐⭐ 非常适合入门！

---

### 2. Crazepony ⭐⭐⭐⭐

#### 简介
- 专门为学习设计的迷你四轴
- 配套教程详细
- 代码注释多
- 硬件小巧安全

#### 特点
- 配套的四轴很小，摔了不心疼
- 有视频教程
- 有文字教程

#### GitHub
- https://github.com/Crazepony

#### 学习难度
- ⭐⭐ 很友好！

---

### 3. MiniFly

#### 简介
- 另一个学习用的飞控
- STM32的
- 代码量适中

#### GitHub
- 搜一下就能找到

---

## 怎么学这些开源代码？

### 方法一：先搭起来跑 (推荐！)

#### 步骤
1. **买个支持的飞控**
   - F4飞控 (¥150-250) → 刷BetaFlight
   - 或者Pixhawk (¥300-500) → 刷PX4/APM

2. **装好地面站**
   - BetaFlight: BetaFlight Configurator (Chrome插件/软件)
   - PX4: QGroundControl
   - APM: Mission Planner

3. **按教程校准**
   - 加速度计
   - 指南针
   - 遥控器
   - 电调

4. **飞起来！**
   - 先在模拟器练
   - 再实际飞

---

### 方法二：代码读起来

#### 如果你想研究BetaFlight
```
建议阅读顺序：
1. src/main/flight/imu.c      → 陀螺仪读取
2. src/main/flight/pid.c      → PID控制
3. src/main/flight/mixer.c    → 电机混控
4. src/main/flight/imu.c      → 姿态解算
```

#### 如果你想研究PX4
```
PX4用了NuttX实时操作系统
代码结构更大更规范
建议：
1. 先看 docs.px4.io 的文档
2. 再看 src/modules 的模块
3. 可以用仿真 (SITL) 在电脑上跑
```

---

### 方法三：修改小功能 (实践出真知！)

#### 可以尝试的小改动
1. **改LED闪烁**
   - 让LED按你想要的方式闪
   - 最简单！

2. **改PID默认参数**
   - 找到pid.c里的默认值
   - 改成你觉得好的
   - 编译刷进去试试

3. **加个新的飞行模式**
   - 稍微难一点
   - 但很有成就感

4. **改OSD显示内容**
   - 把你想显示的信息加上去

---

## 🛠️ 开发环境搭建

### 对于BetaFlight
```
1. 安装 BetaFlight Configurator
2. 安装 ARM GCC 编译器
3. 克隆代码: git clone https://github.com/betaflight/betaflight
4. 按说明编译

或者直接用在线编译服务！
```

### 对于PX4
```
PX4的开发环境稍微复杂一点
但是文档超级详细！
1. 看 https://docs.px4.io 的开发指南
2. 安装工具链
3. 可以直接在电脑仿真 (SITL)，不用硬件！
```

---

## 📚 推荐学习顺序

### 如果你是纯新手，想先飞再说
1. ✅ 买F4飞控
2. ✅ 刷BetaFlight
3. ✅ 装BetaFlight Configurator
4. ✅ 校准，飞！
5. ✅ 等你飞熟了再看代码

### 如果你想先从代码学起
1. ✅ 先看MultiWii代码 (简单！)
2. ✅ 理解基本原理
3. ✅ 再看BetaFlight
4. ✅ 最后看PX4/APM (大而全)

---

## 💡 我的推荐

### 想先玩，再学
→ **买F4飞控 + BetaFlight**

### 想学代码，但想从简单的开始
→ **看MultiWii代码**

### 想深入学，以后做专业开发
→ **买Pixhawk + PX4**

---

## 你想从哪个开始？

1. 先买飞控玩着，看BetaFlight
2. 先看MultiWii代码学习原理
3. 买Pixhawk学PX4，一步到位

你倾向于哪个？
