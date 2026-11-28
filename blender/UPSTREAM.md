# Blender source snapshot

Source: [KosmX/emotes, dev/blender](https://github.com/KosmX/emotes/tree/4f7d946ef537cf75ab54f021f140bc75456c89d2/blender).

Pinned commit: `4f7d946ef537cf75ab54f021f140bc75456c89d2`, including the August 2026 Blender changes from upstream PRs #877 and #878.

The Blender project, export script, export_functions modules, and upstream README are unmodified copies. The upstream GPL-3.0 license is included as `LICENSE`; this directory keeps its upstream licensing. The repository's existing MIT license applies to its own tools, not to these copied Blender files.

Use Blender 5.2 or newer. Upstream targets PAL 1.2.5+mc.26.2 or newer. The older legacy Blender project and script have been organized into `blender/legacy/` (`emote_creator_bend_item_scale.blend` and `emote_blender_exporter_legacy.py`) for older workflows.

Validation used Blender 5.2.1 with automatic script execution disabled at load, followed by explicit execution of the inspected exporter. The `cartwheel` action exported successfully, including animation-local `model`/`parents`, `loopTick`, PAL metadata and icon data. Export restored the original action and action slot and did not leave temporary actions behind.

The Blockbench plugin imports the resulting JSON. When the source rig differs from the current project, its curved tracks are sampled at 60 samples per second before hierarchy conversion. A model without matching custom bones keeps their animation tracks; those bones do not gain geometry automatically.
