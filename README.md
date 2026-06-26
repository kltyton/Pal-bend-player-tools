# PAL Bend Player Tools

Blockbench 插件 + Python 转换脚本，用于编辑 PlayerAnimationLibrary / Emotecraft 玩家动画，并支持 `*_bend` 辅助骨骼弯曲。

## 文件

- `pal_bend_player_tools.js`：Blockbench 插件，内置普通版和“龙核玩家模型版” `player_model.geo.json`，可直接创建玩家动画项目、导入动画、导出动画。
- `player_model.geo.bbmodel`：Blockbench 玩家动画项目模板。
- `player_model.geo.json`：对应的 Minecraft Bedrock geometry。
- `player_model.geo.png`：玩家模型默认纹理。插件新建项目时会自动加载，并命名为 `player_model.geo.png`。
- `pal_source_lib.py`：Python 转换核心库。
- `emote_to_animations.py`：emote -> PAL bend animations；可选输出 `player_model.geo` helper-bend 格式。
- `animations_to_emote.py`：PAL bend animations / `player_model.geo` helper-bend animations -> emote。
- `traditional_bend_to_pal_bend.py`：`*_bend.rotation.x` helper-bend animations -> PAL `bend` 字段 animations。

## 模型约定

`player_model.geo` 使用这些辅助骨骼：

```text
torso_bend
right_arm_bend
left_arm_bend
right_leg_bend
left_leg_bend
```

模型保持原始项目层级：

```text
right_item -> right_arm_bend
left_item  -> left_arm_bend
```

本项目默认使用同号 bend 约定：

```text
player_model.geo helper rotation.x/y/z = PAL bend degrees x/y/z
PAL bend degrees x/y/z = player_model.geo helper rotation.x/y/z
```

Python 脚本里对应参数是 `--helper-sign 1`，这是默认值。只有你明确需要反向时才使用 `--helper-sign -1`。

## Blockbench 插件用法

把 `pal_bend_player_tools.js` 放到 Blockbench 插件目录，或在 Blockbench 的插件管理器中从文件加载。

Windows 默认插件目录示例：

```text
C:\Users\<用户名>\AppData\Roaming\Blockbench\plugins
```

安装后在 `File > New` / `文件 > 新建` 打开的新建项目格式列表里会出现：

```text
PAL Bend Player Animation
PAL Bend Player Animation - 龙核玩家模型版
```

安装后在 `File > New` / `文件 > 新建` 和 `Tools` / `工具` 菜单里还会出现：

```text
PAL Bend Player Animation
PAL Bend Player Animation - 龙核玩家模型版
```

安装后在 `File > Import` / `文件 > 导入` 菜单里会出现：

```text
PAL: Import Player Animation
```

进入动画模式后，插件也会尝试在左侧动画窗口的原生“导入动画文件”按钮旁添加同一个 PAL 导入按钮；如果当前 Blockbench 内部工具栏接口不可用，则仍以 `File > Import` 为准。

安装后在 `File > Export` / `文件 > 导出` 菜单里会出现：

```text
PAL: Export Player Animation
PAL: Export Bundled player_model.geo.json
```

### 新建玩家动画项目

使用插件内置的 `player_model.geo.json` 创建项目。这个模型包含原始玩家骨骼和 5 个 `*_bend` 辅助骨骼，可直接在 Blockbench 时间轴里预览弯曲。插件会同时加载默认纹理 `player_model.geo.png`。

### 龙核玩家模型版

龙核玩家模型版使用 `方便操作的分组模型.json` 的组名、父子关系和 pivot，例如 `root`、`Body_Lower`、`Body`、`Left_Arm_Lower`、`Right_Hand` 等；导入导出时插件会自动在龙核组名和 PAL 骨骼名之间转换。

### 导入动画

支持导入：

- emote JSON；
- PAL `bend` 字段 animations；
- 已经带 `*_bend` helper 骨骼的 `player_model.geo` animations；
- 使用 `方便操作的分组模型.json` 组名制作的龙核旧 animations，例如 `Body_Lower`、`Body`、`Right_Arm_Lower`、`Left_Leg_Lower`。

导入后会统一转换为 `player_model.geo` 可编辑格式，也就是：

```text
right_arm.bend x/y/z -> right_arm_bend.rotation.x/y/z
left_arm.bend x/y/z  -> left_arm_bend.rotation.x/y/z
torso.bend x/y/z     -> torso_bend.rotation.x/y/z
```

导入时插件会把 PAL / Emotecraft 的默认南向动画校正到当前 `player_model.geo` 的北向预览坐标：`rotation.x/y` 和 `bend` 会在导入时校正，导出时再镜像回 PAL 使用的方向；`position` 位移值会保持原始符号。

导入龙核旧 animations 到普通 PAL 项目时，插件会先按龙核友好 rig 烘焙成平铺 PAL，再反向解烘焙回当前项目的本地父子轨道。导入平铺 PAL / emote 到带父子关系的玩家项目时，也会反向解烘焙回当前项目；已带 `*_bend` helper 的本地模型动画不会做这一步。

注意：本插件会导入/导出 `*_bend.rotation.x/y/z` 与 PAL 原生 `bend`。只有 X 轴变化时仍导出原版 scalar / `post` X 格式；存在 Y/Z 旋转时导出 `[x, y, z]` 向量 bend，供 PlayerAnimationLibraryMoreRotation 使用。Emotecraft emote 仍只有单个 `bend` 字段，因此导出 emote 时只写 X 轴 bend。

### 导出动画

导出时会先把当前 `player_model.geo` helper 动画转换为 PAL bend animations：

```text
right_arm_bend.rotation.x/y/z -> right_arm.bend x/y/z
left_arm_bend.rotation.x/y/z  -> left_arm.bend x/y/z
torso_bend.rotation.x/y/z     -> torso.bend x/y/z
```

导出前插件会按当前 Blockbench 项目的父子关系和 pivot，把 `body`、`torso`、`*_bend` 等父级继承烘焙进 PAL 的平铺骨骼轨道里；因此龙核玩家模型版仍会导出为传统平铺 PAL 骨骼名。

然后按选择导出：

- `传统 PAL bend animations`：导出带 `bend` 字段的 animations JSON；
- `Emotecraft / PAL emote`：在 PAL bend animations 的基础上继续转成 emote JSON。

注意：emote 一次导出一个动画，请先在 Blockbench 中选中目标动画。

## Python 用法

### emote -> PAL bend animations

```bash
python emote_to_animations.py input.emote.json output.animation.json --no-model-format
```

### emote -> player_model.geo helper-bend animations

```bash
python emote_to_animations.py input.emote.json output.model.animation.json --model-format
```

不加 `--model-format` / `--no-model-format` 时，脚本会在交互式终端里询问是否转换为 `player_model.geo.json` 可用格式。

### PAL bend / helper-bend animations -> emote

```bash
python animations_to_emote.py input.animation.json output.emote.json --name animation_name
```

如果输入里检测到 `*_bend` helper 骨骼，脚本会自动先按 `player_model.geo` 模型格式转成 PAL bend。

### helper-bend animations -> PAL bend animations

```bash
python traditional_bend_to_pal_bend.py input.model.animation.json output.pal_bend.animation.json --no-catmullrom
```

如果希望缺少插值信息的 bend 关键帧补成 `catmullrom`：

```bash
python traditional_bend_to_pal_bend.py input.model.animation.json output.pal_bend.animation.json --catmullrom
```

## 注意

这些脚本按 PAL loader 的语义做转换：rotation/bend 常量在 animations 中以度数保存，进入 PAL 后会变成弧度；emote 默认输出 `version=3` 和 `easeBeforeKeyframe=true`，避免旧 emote easing 位移造成的偏差。
