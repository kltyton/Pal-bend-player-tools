# PAL Bend Player Tools

Blockbench 插件 + Python 转换脚本，用于编辑 PlayerAnimationLibrary / Emotecraft 玩家动画，并支持 `*_bend` 辅助骨骼弯曲。

## 文件

- `pal_bend_player_tools.js`：Blockbench 插件。
- `player_model.geo.bbmodel`：Blockbench 玩家动画项目模板。
- `player_model.geo.json`：对应的 Minecraft Bedrock geometry。
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
player_model.geo helper rotation.x = PAL bend degrees
PAL bend degrees = player_model.geo helper rotation.x
```

Python 脚本里对应参数是 `--helper-sign 1`，这是默认值。只有你明确需要反向时才使用 `--helper-sign -1`。

## Blockbench 插件用法

把 `pal_bend_player_tools.js` 放到 Blockbench 插件目录，或在 Blockbench 的插件管理器中从文件加载。

安装后在 `Tools` 菜单里会出现：

```text
PAL：新建玩家动画项目
PAL：导入 animations/emote 到玩家模型
PAL：导出 animations/emote
PAL：导出内置 player_model.geo.json
```

### 新建玩家动画项目

使用内置 `player_model.geo.bbmodel` 创建项目。

### 导入动画

支持导入：

- emote JSON；
- PAL/Bedrock animations JSON；
- PAL `bend` 字段 animations；
- 已经带 `*_bend` helper 骨骼的 `player_model.geo` animations。

导入后会统一转换为 `player_model.geo` 可编辑格式，也就是：

```text
right_arm.bend -> right_arm_bend.rotation.x
left_arm.bend  -> left_arm_bend.rotation.x
torso.bend     -> torso_bend.rotation.x
```

### 导出动画

导出时会先把当前 `player_model.geo` helper 动画转换为 PAL bend animations：

```text
right_arm_bend.rotation.x -> right_arm.bend
left_arm_bend.rotation.x  -> left_arm.bend
torso_bend.rotation.x     -> torso.bend
```

然后按选择导出：

- `animations`：导出 PAL bend animations；
- `emote`：在 PAL bend animations 的基础上继续转成 Emotecraft/PAL emote。

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
