(() => {
    const PLUGIN_ID = "pal_bend_player_tools";
    const SKIP = "pal.skip";
    const EPS_TICK = 0.001;
    const DEFAULT_EASING = "linear";
    const HELPER_SUFFIX = "_bend";
    const BEND_HELPER_BONES = {
        torso: "torso_bend",
        right_arm: "right_arm_bend",
        left_arm: "left_arm_bend",
        right_leg: "right_leg_bend",
        left_leg: "left_leg_bend"
    };
    const DEFAULT_VALUES = {
        right_arm: [-5, 2, 0],
        left_arm: [5, 2, 0],
        left_leg: [1.9, 12, 0.1],
        right_leg: [-1.9, 12, 0.1]
    };
    const TRANSFORM_AXES = {
        position: ["x", "y", "z"],
        rotation: ["pitch", "yaw", "roll"],
        scale: ["scaleX", "scaleY", "scaleZ"],
        bend: ["bend"]
    };
    const ANIM_TRANSFORMS = ["position", "rotation", "scale", "bend"];
    const EASING_NAMES = {
        linear: "LINEAR",
        constant: "CONSTANT",
        step: "STEP",
        easeinsine: "EASEINSINE",
        easeoutsine: "EASEOUTSINE",
        easeinoutsine: "EASEINOUTSINE",
        easeinquad: "EASEINQUAD",
        easeoutquad: "EASEOUTQUAD",
        easeinoutquad: "EASEINOUTQUAD",
        easeincubic: "EASEINCUBIC",
        easeoutcubic: "EASEOUTCUBIC",
        easeinoutcubic: "EASEINOUTCUBIC",
        easeinquart: "EASEINQUART",
        easeoutquart: "EASEOUTQUART",
        easeinoutquart: "EASEINOUTQUART",
        easeinquint: "EASEINQUINT",
        easeoutquint: "EASEOUTQUINT",
        easeinoutquint: "EASEINOUTQUINT",
        easeinexpo: "EASEINEXPO",
        easeoutexpo: "EASEOUTEXPO",
        easeinoutexpo: "EASEINOUTEXPO",
        easeincirc: "EASEINCIRC",
        easeoutcirc: "EASEOUTCIRC",
        easeinoutcirc: "EASEINOUTCIRC",
        easeinback: "EASEINBACK",
        easeoutback: "EASEOUTBACK",
        easeinoutback: "EASEINOUTBACK",
        easeinelastic: "EASEINELASTIC",
        easeoutelastic: "EASEOUTELASTIC",
        easeinoutelastic: "EASEINOUTELASTIC",
        easeinbounce: "EASEINBOUNCE",
        easeoutbounce: "EASEOUTBOUNCE",
        easeinoutbounce: "EASEINOUTBOUNCE",
        catmullrom: "CATMULLROM",
        bezier: "BEZIER"
    };
    const ANIM_EASING_PRETTY = {
        linear: "linear",
        constant: "constant",
        step: "step",
        catmullrom: "catmullrom",
        bezier: "bezier",
        easeinsine: "easeInSine",
        easeoutsine: "easeOutSine",
        easeinoutsine: "easeInOutSine",
        easeinquad: "easeInQuad",
        easeoutquad: "easeOutQuad",
        easeinoutquad: "easeInOutQuad",
        easeincubic: "easeInCubic",
        easeoutcubic: "easeOutCubic",
        easeinoutcubic: "easeInOutCubic",
        easeinquart: "easeInQuart",
        easeoutquart: "easeOutQuart",
        easeinoutquart: "easeInOutQuart",
        easeinquint: "easeInQuint",
        easeoutquint: "easeOutQuint",
        easeinoutquint: "easeInOutQuint",
        easeinexpo: "easeInExpo",
        easeoutexpo: "easeOutExpo",
        easeinoutexpo: "easeInOutExpo",
        easeincirc: "easeInCirc",
        easeoutcirc: "easeOutCirc",
        easeinoutcirc: "easeInOutCirc",
        easeinback: "easeInBack",
        easeoutback: "easeOutBack",
        easeinoutback: "easeInOutBack",
        easeinelastic: "easeInElastic",
        easeoutelastic: "easeOutElastic",
        easeinoutelastic: "easeInOutElastic",
        easeinbounce: "easeInBounce",
        easeoutbounce: "easeOutBounce",
        easeinoutbounce: "easeInOutBounce"
    };
    const PLAYER_MODEL_GEO = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.unknown",
                    "texture_width": 64,
                    "texture_height": 64,
                    "visible_bounds_width": 3,
                    "visible_bounds_height": 3.5,
                    "visible_bounds_offset": [0, 1.25, 0]
                },
                "bones": [
                    {"name": "body", "pivot": [0, 12, 0]},
                    {"name": "torso", "parent": "body", "pivot": [0, 24, 0], "cubes": [{"origin": [-4, 18, -2], "size": [8, 6, 4], "uv": {"north": {"uv": [20, 20], "uv_size": [8, 6]}, "east": {"uv": [16, 20], "uv_size": [4, 6]}, "south": {"uv": [32, 20], "uv_size": [8, 6]}, "west": {"uv": [28, 20], "uv_size": [4, 6]}, "up": {"uv": [20, 16], "uv_size": [8, 4]}, "down": {"uv": [28, 20], "uv_size": [8, -4]}}}]},
                    {"name": "torso_bend", "parent": "torso", "pivot": [0, 18, 0], "cubes": [{"origin": [-4, 12, -2], "size": [8, 6, 4], "uv": {"north": {"uv": [20, 26], "uv_size": [8, 6]}, "east": {"uv": [16, 26], "uv_size": [4, 6]}, "south": {"uv": [32, 26], "uv_size": [8, 6]}, "west": {"uv": [28, 26], "uv_size": [4, 6]}, "up": {"uv": [20, 16], "uv_size": [8, 4]}, "down": {"uv": [28, 20], "uv_size": [8, -4]}}}]},
                    {"name": "head", "parent": "body", "pivot": [0, 24, 0], "cubes": [{"origin": [-4, 24, -4], "size": [8, 8, 8], "uv": {"north": {"uv": [8, 8], "uv_size": [8, 8]}, "east": {"uv": [0, 8], "uv_size": [8, 8]}, "south": {"uv": [24, 8], "uv_size": [8, 8]}, "west": {"uv": [16, 8], "uv_size": [8, 8]}, "up": {"uv": [8, 0], "uv_size": [8, 8]}, "down": {"uv": [16, 8], "uv_size": [8, -8]}}}]},
                    {"name": "right_arm", "parent": "body", "pivot": [-5, 22, 0], "cubes": [{"origin": [-8, 18, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [44, 20], "uv_size": [4, 6]}, "east": {"uv": [40, 20], "uv_size": [4, 6]}, "south": {"uv": [52, 20], "uv_size": [4, 6]}, "west": {"uv": [48, 20], "uv_size": [4, 6]}, "up": {"uv": [44, 16], "uv_size": [4, 4]}, "down": {"uv": [48, 20], "uv_size": [4, -4]}}}]},
                    {"name": "right_arm_bend", "parent": "right_arm", "pivot": [-5, 18, 0], "cubes": [{"origin": [-8, 12, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [44, 26], "uv_size": [4, 6]}, "east": {"uv": [40, 26], "uv_size": [4, 6]}, "south": {"uv": [52, 26], "uv_size": [4, 6]}, "west": {"uv": [48, 26], "uv_size": [4, 6]}, "up": {"uv": [44, 16], "uv_size": [4, 4]}, "down": {"uv": [48, 20], "uv_size": [4, -4]}}}]},
                    {"name": "right_item", "parent": "right_arm_bend", "pivot": [-6, 12, -2], "cubes": [{"origin": [-6, 12.25, -11], "size": [0, 4, 11], "uv": {"north": {"uv": [32, 4], "uv_size": [0, 0]}, "east": {"uv": [32, 4], "uv_size": [0, 0]}, "south": {"uv": [32, 4], "uv_size": [0, 0]}, "west": {"uv": [32, 4], "uv_size": [0, 0]}, "up": {"uv": [32, 4], "uv_size": [0, 0]}, "down": {"uv": [32, 4], "uv_size": [0, 0]}}}]},
                    {"name": "left_arm", "parent": "body", "pivot": [5, 22, 0], "cubes": [{"origin": [4, 18, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [36, 52], "uv_size": [4, 6]}, "east": {"uv": [32, 52], "uv_size": [4, 6]}, "south": {"uv": [44, 52], "uv_size": [4, 6]}, "west": {"uv": [40, 52], "uv_size": [4, 6]}, "up": {"uv": [36, 48], "uv_size": [4, 4]}, "down": {"uv": [40, 52], "uv_size": [4, -4]}}}]},
                    {"name": "left_arm_bend", "parent": "left_arm", "pivot": [5, 18, 0], "cubes": [{"origin": [4, 12, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [36, 58], "uv_size": [4, 6]}, "east": {"uv": [32, 58], "uv_size": [4, 6]}, "south": {"uv": [44, 58], "uv_size": [4, 6]}, "west": {"uv": [40, 58], "uv_size": [4, 6]}, "up": {"uv": [36, 48], "uv_size": [4, 4]}, "down": {"uv": [40, 52], "uv_size": [4, -4]}}}]},
                    {"name": "left_item", "parent": "left_arm_bend", "pivot": [6, 12, -2], "cubes": [{"origin": [6, 12.25, -11], "size": [0, 4, 11], "uv": {"north": {"uv": [33, 4], "uv_size": [0, 0]}, "east": {"uv": [33, 4], "uv_size": [0, 0]}, "south": {"uv": [33, 4], "uv_size": [0, 0]}, "west": {"uv": [33, 4], "uv_size": [0, 0]}, "up": {"uv": [33, 4], "uv_size": [0, 0]}, "down": {"uv": [33, 4], "uv_size": [0, 0]}}}]},
                    {"name": "right_leg", "parent": "body", "pivot": [-2, 12, 0], "cubes": [{"origin": [-4, 6, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [4, 20], "uv_size": [4, 6]}, "east": {"uv": [0, 20], "uv_size": [4, 6]}, "south": {"uv": [12, 20], "uv_size": [4, 6]}, "west": {"uv": [8, 20], "uv_size": [4, 6]}, "up": {"uv": [4, 16], "uv_size": [4, 4]}, "down": {"uv": [8, 20], "uv_size": [4, -4]}}}]},
                    {"name": "right_leg_bend", "parent": "right_leg", "pivot": [-2, 6, 0], "cubes": [{"origin": [-4, 0, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [4, 26], "uv_size": [4, 6]}, "east": {"uv": [0, 26], "uv_size": [4, 6]}, "south": {"uv": [12, 26], "uv_size": [4, 6]}, "west": {"uv": [8, 26], "uv_size": [4, 6]}, "up": {"uv": [4, 16], "uv_size": [4, 4]}, "down": {"uv": [8, 20], "uv_size": [4, -4]}}}]},
                    {"name": "left_leg", "parent": "body", "pivot": [2, 12, 0], "cubes": [{"origin": [0, 6, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [20, 52], "uv_size": [4, 6]}, "east": {"uv": [16, 52], "uv_size": [4, 6]}, "south": {"uv": [28, 52], "uv_size": [4, 6]}, "west": {"uv": [24, 52], "uv_size": [4, 6]}, "up": {"uv": [20, 48], "uv_size": [4, 4]}, "down": {"uv": [24, 52], "uv_size": [4, -4]}}}]},
                    {"name": "left_leg_bend", "parent": "left_leg", "pivot": [2, 6, 0], "cubes": [{"origin": [0, 0, -2], "size": [4, 6, 4], "uv": {"north": {"uv": [20, 58], "uv_size": [4, 6]}, "east": {"uv": [16, 58], "uv_size": [4, 6]}, "south": {"uv": [28, 58], "uv_size": [4, 6]}, "west": {"uv": [24, 58], "uv_size": [4, 6]}, "up": {"uv": [20, 48], "uv_size": [4, 4]}, "down": {"uv": [24, 52], "uv_size": [4, -4]}}}]}
                ]
            }
        ]
    };

    let actions = [];

    Plugin.register(PLUGIN_ID, {
        title: "PAL Bend Player Tools",
        author: "fufufuns",
        icon: "accessibility_new",
        description: "Edit PAL / Emotecraft player animations with player_model.geo helper bend bones.",
        tags: ["Animation", "Minecraft: Bedrock Edition"],
        version: "0.1.0",
        variant: "both",
        onload() {
            actions = [
                new Action("pal_bend_new_player_project", {
                    name: "PAL：新建玩家动画项目",
                    description: "使用内置 player_model.geo.json 创建可编辑玩家动画项目",
                    icon: "accessibility_new",
                    click: createPlayerProject
                }),
                new Action("pal_bend_import_animation", {
                    name: "PAL：导入 animations/emote 到玩家模型",
                    description: "导入 PAL bend animations 或 Emotecraft emote，并转换为 *_bend.rotation.x",
                    icon: "file_upload",
                    click: importAnimationFile
                }),
                new Action("pal_bend_export_animation", {
                    name: "PAL：导出 animations/emote",
                    description: "从当前 helper-bend 动画导出 PAL bend animations 或 Emotecraft emote",
                    icon: "file_download",
                    condition: () => typeof Animation !== "undefined" && Animation.all && Animation.all.length > 0,
                    click: showExportDialog
                }),
                new Action("pal_bend_export_geo", {
                    name: "PAL：导出内置 player_model.geo.json",
                    description: "导出插件内置的玩家辅助弯曲模型",
                    icon: "archive",
                    click: exportBuiltInGeo
                })
            ];
            actions.forEach(action => MenuBar.menus.tools.addAction(action));
        },
        onunload() {
            actions.forEach(action => action.delete());
            actions = [];
        }
    });

    function createPlayerProject() {
        const content = prettyJson(PLAYER_MODEL_GEO);
        try {
            if (typeof loadModelFile === "function") {
                loadModelFile({
                    content,
                    path: "player_model.geo.json"
                });
            } else if (globalThis.Codecs && Codecs.bedrock && typeof Codecs.bedrock.parse === "function") {
                Codecs.bedrock.parse(JSON.parse(content), "player_model.geo.json");
            } else {
                createPlayerProjectFallback();
            }
            Blockbench.showQuickMessage("已创建 player_model.geo 玩家动画项目", 1800);
        } catch (error) {
            console.error(error);
            Blockbench.showMessageBox({
                title: "PAL Bend Player Tools",
                message: "创建玩家动画项目失败：" + error.message
            });
        }
    }

    function createPlayerProjectFallback() {
        if (Formats && Formats.bedrock && typeof Formats.bedrock.select === "function") {
            Formats.bedrock.select();
        }
        if (Project) {
            Project.name = "player_model.geo";
            Project.geometry_name = "geometry.unknown";
            Project.texture_width = 64;
            Project.texture_height = 64;
        }
        const geometry = PLAYER_MODEL_GEO["minecraft:geometry"][0];
        const groupMap = {};
        geometry.bones.forEach(bone => {
            const parent = bone.parent ? groupMap[bone.parent] : undefined;
            const group = new Group({
                name: bone.name,
                origin: clone(bone.pivot || [0, 0, 0])
            }).addTo(parent);
            group.init();
            groupMap[bone.name] = group;
            (bone.cubes || []).forEach((cubeData, index) => {
                const from = clone(cubeData.origin || [0, 0, 0]);
                const size = clone(cubeData.size || [0, 0, 0]);
                const cube = new Cube({
                    name: bone.name + (index ? "_" + index : ""),
                    from,
                    to: [from[0] + size[0], from[1] + size[1], from[2] + size[2]]
                }).addTo(group);
                cube.init();
            });
        });
        Canvas.updateAll();
    }

    function exportBuiltInGeo() {
        Blockbench.export({
            type: "Minecraft Bedrock Geometry",
            extensions: ["json"],
            name: "player_model.geo.json",
            savetype: "text",
            content: prettyJson(PLAYER_MODEL_GEO)
        });
    }

    function importAnimationFile() {
        Blockbench.import({
            type: "PAL / Emotecraft Animation",
            extensions: ["json", "emote"],
            readtype: "text",
            multiple: false
        }, files => {
            if (!files || !files[0]) return;
            let data;
            try {
                data = parseJson(files[0].content);
            } catch (error) {
                showError("无法解析 JSON：" + error.message);
                return;
            }
            try {
                const fileBase = baseName(files[0].name || files[0].path || "animation").replace(/\.[^.]+$/, "");
                let animationsJson;
                if (data && data.emote) {
                    const ir = parseEmoteToIR(data, fileBase);
                    animationsJson = irToAnimationsJson(ir, safeAnimationName(data.name || fileBase || "animation"));
                } else if (data && data.animations) {
                    animationsJson = clone(data);
                } else {
                    showError("文件不是 emote JSON，也不是带 animations 字段的动画 JSON。");
                    return;
                }
                const modelAnimations = convertToBendableModelFormat(animationsJson, {
                    keepPalBend: false,
                    helperSign: 1
                });
                const result = loadAnimationsIntoProject(modelAnimations);
                Blockbench.showQuickMessage(`已导入 ${result.created} 个动画${result.missing ? `，${result.missing} 个骨骼未匹配` : ""}`, 2600);
            } catch (error) {
                console.error(error);
                showError("导入动画失败：" + error.message);
            }
        });
    }

    function showExportDialog() {
        const selectedName = Animation.selected ? Animation.selected.name : "";
        const dialog = new Dialog({
            id: "pal_bend_export_dialog",
            title: "PAL 导出动画",
            form: {
                format: {
                    label: "导出类型",
                    type: "select",
                    default: "animations",
                    options: {
                        animations: "传统 PAL bend animations",
                        emote: "Emotecraft / PAL emote"
                    }
                },
                scope: {
                    label: "动画范围",
                    type: "select",
                    default: selectedName ? "selected" : "all",
                    options: {
                        selected: "当前选中动画",
                        all: "全部动画"
                    }
                },
                emote_name: {
                    label: "Emote 名称",
                    type: "text",
                    value: selectedName || "animation"
                },
                author: {
                    label: "作者",
                    type: "text",
                    value: ""
                },
                description: {
                    label: "描述",
                    type: "text",
                    value: ""
                }
            },
            onConfirm(form) {
                try {
                    exportAnimations(form);
                } catch (error) {
                    console.error(error);
                    showError("导出动画失败：" + error.message);
                }
            }
        });
        dialog.show();
    }

    function exportAnimations(form) {
        const animations = collectAnimations(form.scope);
        if (!animations.length) {
            showError("没有可导出的动画。");
            return;
        }
        if (form.format === "emote" && animations.length !== 1) {
            showError("emote 一次只能导出一个动画，请选择“当前选中动画”。");
            return;
        }

        const modelAnimations = compileAnimationsFromProject(animations);
        const palBendAnimations = modelAnimationsToPalBend(modelAnimations, {
            helperSign: 1,
            keepHelpers: false
        });

        if (form.format === "animations") {
            Blockbench.export({
                type: "PAL Bend Animations",
                extensions: ["json"],
                name: "pal_bend.animation.json",
                savetype: "text",
                content: prettyJson(palBendAnimations)
            });
            return;
        }

        const animationName = Object.keys(palBendAnimations.animations || {})[0];
        const ir = parseAnimationsToIR(palBendAnimations, animationName)[animationName];
        const emote = irToEmoteJson(ir, {
            name: form.emote_name || animationName || "animation",
            author: form.author || "",
            description: form.description || "",
            degrees: false,
            version: 3,
            easeBeforeKeyframe: true
        });
        Blockbench.export({
            type: "Emotecraft / PAL Emote",
            extensions: ["json", "emote"],
            name: safeFileName((form.emote_name || animationName || "animation") + ".emote.json"),
            savetype: "text",
            content: prettyJson(emote)
        });
    }

    function loadAnimationsIntoProject(data) {
        if (!hasPlayerHelperBones()) {
            Blockbench.showMessageBox({
                title: "PAL Bend Player Tools",
                message: "当前项目没有完整的 player_model.geo helper-bend 骨骼。建议先执行“PAL：新建玩家动画项目”。插件仍会导入动画，但缺少骨骼的轨道不会显示。"
            });
        }
        const animations = data.animations || {};
        let created = 0;
        let missing = 0;
        Object.keys(animations).forEach(name => {
            const animObj = animations[name] || {};
            const bbAnimation = new Animation({
                name: uniqueAnimationName(name),
                length: numberOr(animObj.animation_length, 0),
                snapping: 20,
                loop: animObj.loop === true || String(animObj.loop).toLowerCase() === "true" ? "loop" : "once"
            }).add();
            if (typeof bbAnimation.init === "function") bbAnimation.init();
            const bones = animObj.bones || {};
            Object.keys(bones).forEach(boneName => {
                const group = findGroupByName(boneName);
                if (!group) {
                    missing += 1;
                    return;
                }
                const animator = getAnimatorForGroup(group, bbAnimation, boneName);
                const bone = bones[boneName] || {};
                ["position", "rotation", "scale"].forEach(channel => {
                    if (bone[channel]) addJsonTrackToAnimator(animator, channel, bone[channel]);
                });
            });
            if (typeof bbAnimation.calculateSnappingFromKeyframes === "function") {
                bbAnimation.calculateSnappingFromKeyframes();
            }
            if (created === 0 && typeof bbAnimation.select === "function") {
                bbAnimation.select();
            }
            created += 1;
        });
        if (globalThis.Modes && Modes.animate && typeof Modes.animate.select === "function") {
            Modes.animate.select();
        }
        if (globalThis.Animator && typeof Animator.preview === "function") {
            Animator.preview();
        }
        return {created, missing};
    }

    function addJsonTrackToAnimator(animator, channel, track) {
        getAnimationEntries(track).forEach(([time, element]) => {
            const key = jsonElementToBlockbenchKey(element, channel);
            if (!key) return;
            const keyframeData = {
                channel,
                time,
                data_points: key.dataPoints
            };
            if (key.easing && key.easing !== DEFAULT_EASING) keyframeData.easing = easingForAnimation(key.easing);
            if (key.interpolation) keyframeData.interpolation = key.interpolation;
            if (key.easingArgs) keyframeData.easingArgs = key.easingArgs;
            animator.addKeyframe(keyframeData);
        });
    }

    function jsonElementToBlockbenchKey(element, channel) {
        let interpolation;
        let easing = DEFAULT_EASING;
        let easingArgs;
        if (element && typeof element === "object" && !Array.isArray(element)) {
            easing = normalizeEasing(element.easing || element.lerp_mode || DEFAULT_EASING);
            easingArgs = element.easingArgs;
            if (element.lerp_mode === "catmullrom") interpolation = "catmullrom";
            if (element.lerp_mode === "bezier" || (element.pre !== undefined && element.post !== undefined)) interpolation = "bezier";
        }
        const dataPoints = [];
        if (element && typeof element === "object" && !Array.isArray(element) && (element.pre !== undefined || element.post !== undefined)) {
            if (element.pre !== undefined) dataPoints.push(vectorDataPoint(valueToVector(element.pre, channel)));
            dataPoints.push(vectorDataPoint(valueToVector(element.post !== undefined ? element.post : element.pre, channel)));
        } else {
            dataPoints.push(vectorDataPoint(valueToVector(element, channel)));
        }
        if (!dataPoints.length) return null;
        return {dataPoints, easing, interpolation, easingArgs};
    }

    function compileAnimationsFromProject(animations) {
        const out = {
            format_version: "1.8.0",
            animations: {}
        };
        animations.forEach(animation => {
            const animObj = {
                animation_length: cleanNumber(numberOr(animation.length, 0)),
                bones: {}
            };
            if (animation.loop === "loop" || animation.loop === true) animObj.loop = true;
            Object.keys(animation.animators || {}).forEach(id => {
                const animator = animation.animators[id];
                if (!animator) return;
                const boneName = animator.name || findGroupNameByUuid(id);
                if (!boneName) return;
                const boneOut = {};
                ["position", "rotation", "scale"].forEach(channel => {
                    const keyframes = Array.isArray(animator[channel]) ? animator[channel] : [];
                    if (keyframes.length) boneOut[channel] = blockbenchKeyframesToTrack(keyframes, channel);
                });
                if (Object.keys(boneOut).length) animObj.bones[boneName] = boneOut;
            });
            out.animations[animation.name || "animation"] = animObj;
        });
        return out;
    }

    function blockbenchKeyframesToTrack(keyframes, channel) {
        const track = {};
        keyframes.slice().sort((a, b) => a.time - b.time).forEach(keyframe => {
            const time = formatSeconds(numberOr(keyframe.time, 0));
            const points = Array.isArray(keyframe.data_points) && keyframe.data_points.length
                ? keyframe.data_points
                : [{x: keyframe.get ? keyframe.get("x") : 0, y: keyframe.get ? keyframe.get("y") : 0, z: keyframe.get ? keyframe.get("z") : 0}];
            const post = dataPointVector(points[points.length - 1], channel);
            const obj = {vector: post};
            if (points.length > 1) {
                obj.pre = dataPointVector(points[0], channel);
                obj.post = post;
                delete obj.vector;
            }
            if (keyframe.interpolation && keyframe.interpolation !== "linear") {
                obj.lerp_mode = keyframe.interpolation;
            }
            if (keyframe.easing && normalizeEasing(keyframe.easing) !== DEFAULT_EASING) {
                obj.easing = easingForAnimation(keyframe.easing);
            }
            track[time] = obj;
        });
        return track;
    }

    function getAnimatorForGroup(group, animation, fallbackName) {
        if (typeof animation.getBoneAnimator === "function") {
            try {
                const animator = animation.getBoneAnimator(group);
                if (animator) return animator;
            } catch (error) {
                console.warn(error);
            }
        }
        if (!animation.animators) animation.animators = {};
        let animator = animation.animators[group.uuid];
        if (!animator) {
            animator = new BoneAnimator(group.uuid, animation, fallbackName || group.name);
            animation.animators[group.uuid] = animator;
            if (typeof animator.init === "function") animator.init();
        }
        return animator;
    }

    function convertToBendableModelFormat(animationsJson, options = {}) {
        const keepPalBend = !!options.keepPalBend;
        const helperSign = options.helperSign === undefined ? 1 : Number(options.helperSign);
        const out = clone(animationsJson);
        Object.values(out.animations || {}).forEach(animObj => {
            if (!animObj || typeof animObj !== "object") return;
            const bones = animObj.bones || {};
            Object.keys(BEND_HELPER_BONES).forEach(parent => {
                const helper = BEND_HELPER_BONES[parent];
                const parentBone = bones[parent];
                if (!parentBone || typeof parentBone !== "object" || parentBone.bend === undefined) return;
                const bendTrack = normalizeTrack(parentBone.bend);
                const helperBone = bones[helper] = bones[helper] && typeof bones[helper] === "object" ? bones[helper] : {};
                const helperRotation = helperBone.rotation = helperBone.rotation && typeof helperBone.rotation === "object" ? helperBone.rotation : {};
                Object.keys(bendTrack).forEach(timestamp => {
                    helperRotation[String(timestamp)] = bendKeyToHelperRotationKey(bendTrack[timestamp], helperSign);
                });
                if (!keepPalBend) delete parentBone.bend;
            });
            removeEmptyBones(bones);
        });
        return out;
    }

    function modelAnimationsToPalBend(data, options = {}) {
        const helperSign = options.helperSign === undefined ? 1 : Number(options.helperSign);
        const keepHelpers = !!options.keepHelpers;
        const out = clone(data);
        Object.values(out.animations || {}).forEach(animObj => {
            const bones = animObj && animObj.bones;
            if (!bones || typeof bones !== "object") return;
            Object.keys(bones).forEach(helperName => {
                if (!helperName.endsWith(HELPER_SUFFIX)) return;
                const helper = bones[helperName];
                if (!helper || typeof helper !== "object" || helper.rotation === undefined) return;
                const baseName = helperName.slice(0, -HELPER_SUFFIX.length);
                const bendTrack = {};
                const rotationTrack = normalizeTrack(helper.rotation);
                Object.keys(rotationTrack).forEach(timestamp => {
                    bendTrack[String(timestamp)] = helperFrameToBendFrame(rotationTrack[timestamp], helperSign);
                });
                const base = bones[baseName] = bones[baseName] && typeof bones[baseName] === "object" ? bones[baseName] : {};
                base.bend = Object.assign({}, base.bend && typeof base.bend === "object" ? clone(base.bend) : {}, bendTrack);
                if (!keepHelpers) {
                    const remaining = clone(helper);
                    delete remaining.rotation;
                    if (Object.keys(remaining).length) bones[helperName] = remaining;
                    else delete bones[helperName];
                }
            });
            removeEmptyBones(bones);
        });
        return out;
    }

    function bendKeyToHelperRotationKey(value, helperSign) {
        const out = {post: [applySign(vectorX(value, 0), helperSign), 0, 0]};
        if (value && typeof value === "object" && !Array.isArray(value) && value.pre !== undefined) {
            out.pre = [applySign(vectorX(value.pre, 0), helperSign), 0, 0];
        }
        const lerp = copyLerpFromKey(value);
        if (lerp !== undefined) out.lerp_mode = lerp;
        return out;
    }

    function helperFrameToBendFrame(frame, helperSign) {
        if (frame && typeof frame === "object" && !Array.isArray(frame)) {
            const out = {};
            if (frame.pre !== undefined) out.pre = applySign(vectorX(frame.pre, 0), helperSign);
            if (frame.post !== undefined) out.post = applySign(vectorX(frame.post, 0), helperSign);
            else if (frame.vector !== undefined || frame.value !== undefined) out.post = applySign(vectorX(frame, 0), helperSign);
            ["lerp_mode", "easing", "easingArgs", "easingX", "easingY", "easingZ", "easingArgsX", "easingArgsY", "easingArgsZ"].forEach(key => {
                if (frame[key] !== undefined) out[key] = clone(frame[key]);
            });
            if (!Object.keys(out).length) out.post = applySign(vectorX(frame, 0), helperSign);
            return out;
        }
        return {post: applySign(vectorX(frame, 0), helperSign)};
    }

    function parseEmoteToIR(data, nameHint) {
        if (!data || !data.emote) throw new Error("not an emote JSON: missing top-level emote");
        const node = data.emote;
        const version = parseInt(data.version === undefined ? 1 : data.version, 10);
        const beginTick = numberOr(node.beginTick, 0);
        let endTick = Math.max(numberOr(node.endTick, beginTick + 1), beginTick + 1);
        const isLoop = typeof node.isLoop === "string" ? node.isLoop.toLowerCase() === "true" : !!node.isLoop;
        const returnTickRaw = node.returnTick !== undefined ? parseInt(node.returnTick, 10) : 0;
        const loopTick = isLoop ? Math.max(returnTickRaw - 1, 0) : null;
        const stopTick = numberOr(node.stopTick, 0);
        if (!isLoop) endTick = stopTick <= endTick ? endTick + 3 : stopTick;
        const ir = createIR(data.name || nameHint || "animation");
        ir.lengthTicks = endTick;
        ir.loop = isLoop;
        ir.loopTick = loopTick;
        ir.metadata = {
            name: data.name || nameHint || "animation",
            author: data.author || "",
            description: data.description || "",
            version,
            beginTick,
            sourceEndTick: numberOr(node.endTick, endTick),
            stopTick,
            degrees: node.degrees !== undefined ? !!node.degrees : true,
            easeBeforeKeyframe: !!node.easeBeforeKeyframe
        };
        const degrees = ir.metadata.degrees;
        const moves = Array.isArray(node.moves) ? node.moves.slice() : [];
        moves.sort((a, b) => parseInt(numberOr(a.tick, 0), 10) - parseInt(numberOr(b.tick, 0), 10));
        moves.forEach(move => {
            const tick = numberOr(move.tick, 0);
            if (tick > endTick) return;
            const easing = normalizeEasing(move.easing || DEFAULT_EASING);
            const turn = parseInt(move.turn || 0, 10);
            Object.keys(move).forEach(rawBoneName => {
                if (["tick", "comment", "easing", "turn"].includes(rawBoneName)) return;
                const partNode = move[rawBoneName];
                if (!partNode || typeof partNode !== "object") return;
                let boneName = getCorrectPlayerBoneName(rawBoneName);
                if (version < 3 && boneName === "torso") boneName = "body";
                boneName = getCorrectPlayerBoneName(boneName);
                const bone = ensureBone(ir, boneName);
                ["x", "y", "z"].forEach((field, index) => {
                    if (partNode[field] !== undefined) {
                        appendAxisKey(bone, "position", field, tick, convertEmoteToInternalValue(boneName, "position", index, partNode[field], degrees, turn), easing);
                    }
                });
                ["pitch", "yaw", "roll"].forEach((field, index) => {
                    if (partNode[field] !== undefined) {
                        appendAxisKey(bone, "rotation", ["x", "y", "z"][index], tick, convertEmoteToInternalValue(boneName, "rotation", index, partNode[field], degrees, turn), easing);
                    }
                });
                ["scaleX", "scaleY", "scaleZ"].forEach((field, index) => {
                    if (partNode[field] !== undefined) {
                        appendAxisKey(bone, "scale", ["x", "y", "z"][index], tick, convertEmoteToInternalValue(boneName, "scale", index, partNode[field], degrees, turn), easing);
                    }
                });
                if (partNode.bend !== undefined) {
                    appendAxisKey(bone, "bend", "x", tick, convertEmoteToInternalValue(boneName, "bend", 0, partNode.bend, degrees, turn), easing);
                }
            });
        });
        const body = ir.bones.body;
        if (body && body.bend.x.length) {
            const torso = ensureBone(ir, "torso");
            torso.bend.x.push(...body.bend.x);
            body.bend.x = [];
            if (!boneHasAnyKeyframes(body)) delete ir.bones.body;
        }
        if (!ir.metadata.easeBeforeKeyframe) {
            Object.values(ir.bones).forEach(correctEasingsForBone);
        }
        Object.keys(ir.bones).forEach(boneName => {
            if (boneName === "right_item" || boneName === "left_item") swapYZKeyframesForItems(ir.bones[boneName]);
        });
        return ir;
    }

    function parseAnimationsToIR(data, animationName) {
        if (!data || !data.animations) throw new Error("not an animations JSON: missing top-level animations");
        const out = {};
        const names = animationName ? [animationName] : Object.keys(data.animations);
        names.forEach(name => {
            const animObj = data.animations[name];
            if (!animObj) throw new Error(`animation ${name} not found`);
            const ir = createIR(name);
            if (animObj.animation_length !== undefined) ir.lengthTicks = numberOr(animObj.animation_length, 0) * 20;
            if (animObj.loopTick !== undefined) {
                ir.loop = true;
                ir.loopTick = numberOr(animObj.loopTick, 0) * 20;
            } else if (animObj.loop === true || String(animObj.loop).toLowerCase() === "true") {
                ir.loop = true;
                ir.loopTick = 0;
            }
            let maxTick = 0;
            const bones = animObj.bones || {};
            Object.keys(bones).forEach(rawBoneName => {
                const boneName = getCorrectPlayerBoneName(rawBoneName);
                const bone = ensureBone(ir, boneName);
                ANIM_TRANSFORMS.forEach(transform => {
                    getAnimationEntries((bones[rawBoneName] || {})[transform]).forEach(([seconds, element]) => {
                        const [vector, easings, args] = elementVectorAndEasing(element);
                        const fullVector = vector.slice();
                        while (fullVector.length < 3) fullVector.push(SKIP);
                        ["x", "y", "z"].forEach((axis, index) => {
                            if (transform === "bend" && axis !== "x") return;
                            const raw = fullVector[index];
                            if (isSkip(raw)) return;
                            const internal = parseAnimValueToInternal(raw, transform);
                            const tick = seconds * 20;
                            bone[transform][axis].push({
                                tick,
                                value: internal,
                                easing: normalizeEasing(easings[axis] || DEFAULT_EASING),
                                easingArgs: args[axis]
                            });
                            maxTick = Math.max(maxTick, tick);
                        });
                    });
                });
            });
            if (!ir.lengthTicks) ir.lengthTicks = maxTick || 0;
            out[name] = ir;
        });
        return out;
    }

    function irToAnimationsJson(ir, animationName) {
        const animName = animationName || ir.name || "animation";
        const bonesOut = {};
        Object.keys(ir.bones).sort().forEach(boneName => {
            const bone = ir.bones[boneName];
            const boneOut = {};
            ANIM_TRANSFORMS.forEach(transform => {
                const stacks = bone[transform];
                const activeAxes = Object.keys(stacks).filter(axis => stacks[axis].length);
                if (!activeAxes.length) return;
                const timeMap = {};
                activeAxes.forEach(axis => {
                    addInitialDefaultKeysForAnimation(stacks[axis], transform).forEach(key => {
                        const entry = timeMap[key.tick] = timeMap[key.tick] || {vector: [SKIP, SKIP, SKIP], axisEasing: {}};
                        const index = {x: 0, y: 1, z: 2}[axis];
                        entry.vector[index] = valueForAnimationJson(key.value, transform);
                        entry.axisEasing[axis] = key.easing;
                    });
                });
                const transformOut = {};
                Object.keys(timeMap).map(Number).sort((a, b) => a - b).forEach(tick => {
                    const entry = timeMap[tick];
                    const used = ["x", "y", "z"].filter((axis, index) => !isSkip(entry.vector[index]));
                    const keyObj = {vector: cleanNumber(entry.vector)};
                    if (used.length) {
                        const vals = used.map(axis => normalizeEasing(entry.axisEasing[axis] || DEFAULT_EASING));
                        if (new Set(vals).size === 1) {
                            if (vals[0] !== DEFAULT_EASING) keyObj.easing = easingForAnimation(vals[0]);
                        } else {
                            used.forEach(axis => {
                                const easing = normalizeEasing(entry.axisEasing[axis] || DEFAULT_EASING);
                                if (easing !== DEFAULT_EASING) keyObj["easing" + axis.toUpperCase()] = easingForAnimation(easing);
                            });
                        }
                    }
                    transformOut[formatSeconds(tick / 20)] = keyObj;
                });
                boneOut[transform] = transformOut;
            });
            if (Object.keys(boneOut).length) bonesOut[boneName] = boneOut;
        });
        const animObj = {
            animation_length: cleanNumber(ir.lengthTicks / 20),
            bones: bonesOut
        };
        if (ir.loop) {
            animObj.loop = true;
            if (ir.loopTick && ir.loopTick > 0) animObj.loopTick = cleanNumber(ir.loopTick / 20);
        }
        return {format_version: "1.8.0", animations: {[animName]: animObj}};
    }

    function irToEmoteJson(ir, options = {}) {
        const moves = [];
        Object.keys(ir.bones).sort().forEach(boneName => {
            const bone = ir.bones[boneName];
            const emoteBoneName = restorePlayerBoneName(boneName);
            ANIM_TRANSFORMS.forEach(transform => {
                const stacks = splitAnimAxisForEmoteItems(boneName, transform, bone[transform]);
                const axes = transform === "bend" ? ["x"] : ["x", "y", "z"];
                const fields = TRANSFORM_AXES[transform];
                axes.forEach((axis, axisIndex) => {
                    (stacks[axis] || []).slice().sort((a, b) => a.tick - b.tick).forEach(key => {
                        const defaultInternal = transform === "scale" ? 1 : 0;
                        if (Math.abs(key.tick) < 1e-9 && isNum(key.value) && Math.abs(Number(key.value) - defaultInternal) < 1e-9) return;
                        const value = convertInternalToEmoteValue(boneName, transform, axisIndex, key.value, !!options.degrees);
                        moves.push({
                            tick: formatTick(key.tick),
                            easing: easingForEmote(key.easing),
                            turn: 0,
                            [emoteBoneName]: {
                                [fields[axisIndex]]: cleanNumber(value)
                            }
                        });
                    });
                });
            });
        });
        moves.sort((a, b) => {
            const tickDelta = numberOr(a.tick, 0) - numberOr(b.tick, 0);
            if (tickDelta) return tickDelta;
            const boneA = Object.keys(a).find(k => !["tick", "easing", "turn"].includes(k)) || "";
            const boneB = Object.keys(b).find(k => !["tick", "easing", "turn"].includes(k)) || "";
            return boneA.localeCompare(boneB);
        });
        const endTick = Number.isFinite(ir.lengthTicks) ? ir.lengthTicks : 0;
        const emote = {
            isLoop: ir.loop ? "true" : "false",
            returnTick: ir.loop ? parseInt((ir.loopTick || 0) + 1, 10) : 2,
            beginTick: 0,
            endTick: cleanNumber(ir.loop ? endTick : Math.max(0, endTick - 3)),
            stopTick: cleanNumber(endTick),
            degrees: !!options.degrees,
            moves
        };
        if (options.easeBeforeKeyframe !== false) emote.easeBeforeKeyframe = true;
        return {
            version: options.version || 3,
            name: options.name || ir.metadata.name || ir.name || "animation",
            author: options.author !== undefined ? options.author : (ir.metadata.author || ""),
            description: options.description !== undefined ? options.description : (ir.metadata.description || ""),
            emote
        };
    }

    function createIR(name) {
        return {
            name: name || "animation",
            lengthTicks: 0,
            loop: false,
            loopTick: null,
            bones: {},
            metadata: {}
        };
    }

    function createBoneIR() {
        return {
            position: {x: [], y: [], z: []},
            rotation: {x: [], y: [], z: []},
            scale: {x: [], y: [], z: []},
            bend: {x: []}
        };
    }

    function ensureBone(ir, boneName) {
        if (!ir.bones[boneName]) ir.bones[boneName] = createBoneIR();
        return ir.bones[boneName];
    }

    function appendAxisKey(bone, transform, axis, tick, value, easing) {
        bone[transform][axis].push({tick: Number(tick), value, easing: normalizeEasing(easing)});
    }

    function correctEasingsForBone(bone) {
        ANIM_TRANSFORMS.forEach(transform => {
            Object.values(bone[transform]).forEach(correctEasingsForAxis);
        });
    }

    function correctEasingsForAxis(keys) {
        if (!keys.length) return;
        let previous = "easeinoutsine";
        keys.forEach(key => {
            const current = key.easing;
            key.easing = previous;
            previous = current;
        });
        const last = keys[keys.length - 1];
        keys.push({tick: last.tick + EPS_TICK, value: last.value, easing: previous});
    }

    function swapYZKeyframesForItems(bone) {
        [bone.position.y, bone.position.z] = [bone.position.z, bone.position.y];
        [bone.rotation.y, bone.rotation.z] = [bone.rotation.z, bone.rotation.y];
    }

    function boneHasAnyKeyframes(bone) {
        return ANIM_TRANSFORMS.some(transform => Object.values(bone[transform]).some(keys => keys.length));
    }

    function getAnimationEntries(element) {
        if (element === undefined || element === null) return [];
        if (isNum(element)) return [[0, [element, element, element]]];
        if (Array.isArray(element)) return [[0, element]];
        if (typeof element === "object") {
            if (element.vector !== undefined) return [[0, element]];
            if (element.value !== undefined) {
                const obj = clone(element);
                obj.vector = [obj.value, 0, 0];
                return [[0, obj]];
            }
            const out = [];
            Object.keys(element).forEach(key => {
                const timestamp = parseTimestamp(key);
                let value = element[key];
                if (value && typeof value === "object" && !Array.isArray(value)) {
                    value = clone(value);
                    if (value.value !== undefined) {
                        value.vector = [value.value, 0, 0];
                        out.push([timestamp, value]);
                        return;
                    }
                    if (value.vector === undefined) {
                        let added = false;
                        if (value.pre !== undefined) {
                            const preVector = extractBedrockKeyframe(value.pre);
                            if (value.easing !== undefined) {
                                const obj = {vector: preVector, easing: value.easing};
                                if (value.easingArgs !== undefined) obj.easingArgs = value.easingArgs;
                                out.push([timestamp === 0 ? timestamp : timestamp - 0.001, obj]);
                            } else {
                                out.push([timestamp === 0 ? timestamp : timestamp - 0.001, preVector]);
                            }
                            added = true;
                        }
                        if (value.post !== undefined) {
                            const postVector = extractBedrockKeyframe(value.post);
                            if (value.lerp_mode !== undefined) out.push([timestamp, {vector: postVector, easing: value.lerp_mode}]);
                            else out.push([timestamp, postVector]);
                            return;
                        }
                        if (added) return;
                    }
                }
                out.push([timestamp, value]);
            });
            out.sort((a, b) => a[0] - b[0]);
            return out;
        }
        return [[0, [element, element, element]]];
    }

    function extractBedrockKeyframe(keyframe) {
        if (Array.isArray(keyframe)) return keyframe;
        if (isNum(keyframe)) return [keyframe, 0, 0];
        if (!keyframe || typeof keyframe !== "object") return [keyframe, keyframe, keyframe];
        if (keyframe.vector !== undefined) return keyframe.vector;
        if (keyframe.pre !== undefined) return Array.isArray(keyframe.pre) ? keyframe.pre : extractBedrockKeyframe(keyframe.pre);
        return Array.isArray(keyframe.post) ? keyframe.post : extractBedrockKeyframe(keyframe.post);
    }

    function elementVectorAndEasing(element) {
        if (Array.isArray(element)) return [element, {}, {}];
        if (element && typeof element === "object") {
            const vector = element.vector !== undefined ? element.vector : extractBedrockKeyframe(element);
            const baseEasing = normalizeEasing(element.easing || DEFAULT_EASING);
            const easings = {};
            const args = {};
            ["X", "Y", "Z"].forEach(letter => {
                const axis = letter.toLowerCase();
                easings[axis] = normalizeEasing(element["easing" + letter] || baseEasing);
                if (element["easingArgs" + letter] !== undefined) args[axis] = element["easingArgs" + letter];
            });
            if (element.easingArgs !== undefined) {
                ["x", "y", "z"].forEach(axis => {
                    if (args[axis] === undefined) args[axis] = element.easingArgs;
                });
            }
            return [vector, easings, args];
        }
        if (isNum(element)) return [[element, element, element], {}, {}];
        return [[element, element, element], {}, {}];
    }

    function parseAnimValueToInternal(value, transform) {
        if (isSkip(value)) return value;
        const isForRotation = transform === "rotation" || transform === "bend";
        if (isNum(value)) return isForRotation ? degToRad(Number(value)) : Number(value);
        if (typeof value === "string") {
            const n = Number(value.trim());
            if (!Number.isNaN(n)) return isForRotation ? degToRad(n) : n;
        }
        return value;
    }

    function valueForAnimationJson(value, transform) {
        if (!isNum(value)) return value;
        if (transform === "rotation" || transform === "bend") return cleanNumber(radToDeg(Number(value)));
        return cleanNumber(Number(value));
    }

    function addInitialDefaultKeysForAnimation(axisKeys, transform) {
        if (!axisKeys.length) return [];
        const keys = axisKeys.slice().sort((a, b) => a.tick - b.tick);
        if (keys[0].tick <= 0) return keys;
        return [{tick: 0, value: transform === "scale" ? 1 : 0, easing: DEFAULT_EASING}, ...keys];
    }

    function convertEmoteToInternalValue(bone, transform, axisIndex, rawValue, degrees, turn) {
        let transformType = null;
        if (transform === "position") transformType = bone === "body" ? "position" : null;
        else if (transform === "rotation") transformType = "rotation";
        else if (transform === "scale") transformType = "scale";
        else if (transform === "bend") transformType = "bend";
        let value = Number(rawValue);
        if (!Number.isFinite(value)) return rawValue;
        if (transformType === null) value -= defaultValues(bone)[axisIndex];
        if (shouldNegateForEmote(bone, transform, axisIndex, transformType)) value *= -1;
        if (transformType === "rotation") {
            if (degrees) value = degToRad(value);
            value += Math.PI * 2 * Number(turn || 0);
        }
        if (transformType === "position") value *= 16;
        return value;
    }

    function convertInternalToEmoteValue(bone, transform, axisIndex, internalValue, degrees) {
        if (!isNum(internalValue)) return internalValue;
        let transformType = null;
        if (transform === "position") transformType = bone === "body" ? "position" : null;
        else if (transform === "rotation") transformType = "rotation";
        else if (transform === "scale") transformType = "scale";
        else if (transform === "bend") transformType = "bend";
        let value = Number(internalValue);
        if (transformType === "position") value /= 16;
        if (transformType === "rotation" && degrees) value = radToDeg(value);
        if (shouldNegateForEmote(bone, transform, axisIndex, transformType)) value *= -1;
        if (transformType === null) value += defaultValues(bone)[axisIndex];
        return value;
    }

    function shouldNegateForEmote(bone, transform, axisIndex, transformType) {
        const isItem = bone === "right_item" || bone === "left_item";
        const isCape = bone === "cape";
        const isBody = bone === "body";
        if (transform === "position" || transform === "rotation") {
            if (axisIndex === 0) return isItem || isCape || isBody;
            if (axisIndex === 1) return isItem || transformType === null || (isBody && transformType === "rotation");
            if (axisIndex === 2) return (isItem && transformType === "rotation") || isCape;
        }
        return false;
    }

    function splitAnimAxisForEmoteItems(boneName, transform, stacks) {
        if ((boneName !== "right_item" && boneName !== "left_item") || (transform !== "position" && transform !== "rotation")) return stacks;
        return {x: stacks.x || [], y: stacks.z || [], z: stacks.y || []};
    }

    function normalizeTrack(track) {
        if (track === undefined || track === null) return {};
        if (typeof track === "object" && !Array.isArray(track)) {
            if (looksLikeSingleKeyframe(track)) return {"0": track};
            return clone(track);
        }
        return {"0": track};
    }

    function looksLikeSingleKeyframe(obj) {
        return obj && typeof obj === "object" && ["vector", "value", "pre", "post", "lerp_mode", "easing"].some(key => obj[key] !== undefined);
    }

    function valueToVector(value, channel) {
        if (value && typeof value === "object" && !Array.isArray(value)) {
            if (value.value !== undefined) return [value.value, 0, 0];
            if (value.vector !== undefined) return valueToVector(value.vector, channel);
            if (value.post !== undefined) return valueToVector(value.post, channel);
            if (value.pre !== undefined) return valueToVector(value.pre, channel);
        }
        if (Array.isArray(value)) {
            const out = value.slice(0, 3);
            while (out.length < 3) out.push(channel === "scale" ? 1 : 0);
            return out;
        }
        if (isNum(value) || typeof value === "string") {
            if (channel === "scale") return [value, value, value];
            return [value, 0, 0];
        }
        return channel === "scale" ? [1, 1, 1] : [0, 0, 0];
    }

    function vectorDataPoint(vector) {
        const point = {};
        ["x", "y", "z"].forEach((axis, index) => {
            if (!isSkip(vector[index])) point[axis] = valueForBlockbench(vector[index]);
        });
        return point;
    }

    function dataPointVector(point, channel) {
        const fallback = channel === "scale" ? 1 : 0;
        return cleanNumber([
            valueFromBlockbench(point && point.x !== undefined ? point.x : fallback),
            valueFromBlockbench(point && point.y !== undefined ? point.y : fallback),
            valueFromBlockbench(point && point.z !== undefined ? point.z : fallback)
        ]);
    }

    function valueForBlockbench(value) {
        if (typeof value === "string") {
            const n = Number(value);
            return Number.isNaN(n) ? value : n;
        }
        return value;
    }

    function valueFromBlockbench(value) {
        if (typeof value === "string") {
            const n = Number(value);
            return Number.isNaN(n) ? value : n;
        }
        return value;
    }

    function vectorX(value, defaultValue) {
        if (value === undefined || value === null) return defaultValue;
        if (isNum(value) || typeof value === "string") return cleanZero(value);
        if (Array.isArray(value)) return value.length ? cleanZero(firstNonSkip(value, defaultValue)) : defaultValue;
        if (typeof value === "object") {
            if (value.value !== undefined) return vectorX(value.value, defaultValue);
            if (value.vector !== undefined) return vectorX(value.vector, defaultValue);
            if (value.post !== undefined) return vectorX(value.post, defaultValue);
            if (value.pre !== undefined) return vectorX(value.pre, defaultValue);
        }
        return defaultValue;
    }

    function firstNonSkip(values, defaultValue) {
        for (const value of values) {
            if (!isSkip(value)) return value;
        }
        return defaultValue;
    }

    function copyLerpFromKey(value) {
        if (!value || typeof value !== "object" || Array.isArray(value)) return undefined;
        const easing = value.lerp_mode !== undefined ? value.lerp_mode : (value.easingX !== undefined ? value.easingX : value.easing);
        if (easing === undefined) return undefined;
        return normalizeEasing(easing) === DEFAULT_EASING ? undefined : easing;
    }

    function applySign(value, sign) {
        if (sign === 1) return value;
        if (isNum(value)) return cleanZero(Number(value) * sign);
        if (typeof value === "string") {
            if (value.trim() === "0" || value.trim() === "0.0") return value;
            return `(${sign})*(${value})`;
        }
        return value;
    }

    function removeEmptyBones(bones) {
        Object.keys(bones).forEach(name => {
            const bone = bones[name];
            if (bone && typeof bone === "object" && !Object.keys(bone).length) delete bones[name];
        });
    }

    function collectAnimations(scope) {
        if (scope === "selected") return Animation.selected ? [Animation.selected] : [];
        return Animation.all ? Animation.all.slice() : [];
    }

    function hasPlayerHelperBones() {
        return Object.values(BEND_HELPER_BONES).every(name => !!findGroupByName(name));
    }

    function findGroupByName(name) {
        if (!globalThis.Group || !Group.all) return null;
        const lower = String(name).toLowerCase();
        return Group.all.find(group => String(group.name).toLowerCase() === lower) || null;
    }

    function findGroupNameByUuid(uuid) {
        if (!globalThis.Group || !Group.all) return "";
        const group = Group.all.find(item => item.uuid === uuid);
        return group ? group.name : "";
    }

    function uniqueAnimationName(name) {
        const base = name || "animation";
        const existing = new Set((Animation.all || []).map(animation => animation.name));
        if (!existing.has(base)) return base;
        let index = 2;
        while (existing.has(`${base}_${index}`)) index += 1;
        return `${base}_${index}`;
    }

    function safeAnimationName(name) {
        return String(name || "animation").trim() || "animation";
    }

    function safeFileName(name) {
        return String(name || "animation.json").replace(/[<>:"/\\|?*]+/g, "_");
    }

    function baseName(path) {
        return String(path || "").split(/[\\/]/).pop() || "animation";
    }

    function parseJson(text) {
        if (typeof autoParseJSON === "function") return autoParseJSON(text, false);
        return JSON.parse(text);
    }

    function prettyJson(data) {
        return JSON.stringify(cleanNumber(data), null, 4) + "\n";
    }

    function clone(value) {
        return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
    }

    function normalizeEasing(value) {
        let key = value === undefined || value === null ? DEFAULT_EASING : String(value);
        key = key.replace(/[_-]/g, "").toLowerCase();
        if (EASING_NAMES[key]) return key;
        const key2 = "ease" + key;
        if (EASING_NAMES[key2]) return key2;
        return DEFAULT_EASING;
    }

    function easingForEmote(easing) {
        return EASING_NAMES[normalizeEasing(easing)] || "LINEAR";
    }

    function easingForAnimation(easing) {
        return ANIM_EASING_PRETTY[normalizeEasing(easing)] || normalizeEasing(easing);
    }

    function getCorrectPlayerBoneName(name) {
        return String(name).replace(/([A-Z])/g, "_$1").toLowerCase();
    }

    function restorePlayerBoneName(name) {
        return String(name).toLowerCase().replace(/_(.)/g, (_match, char) => char.toUpperCase());
    }

    function defaultValues(bone) {
        return DEFAULT_VALUES[bone] || [0, 0, 0];
    }

    function cleanNumber(value) {
        if (typeof value === "number") {
            if (Math.abs(value) < 1e-12) return 0;
            const rounded = Math.round(value * 1e12) / 1e12;
            return Math.abs(rounded - Math.round(rounded)) < 1e-12 ? Math.round(rounded) : rounded;
        }
        if (Array.isArray(value)) return value.map(cleanNumber);
        if (value && typeof value === "object") {
            const out = {};
            Object.keys(value).forEach(key => {
                out[key] = cleanNumber(value[key]);
            });
            return out;
        }
        return value;
    }

    function cleanZero(value) {
        return typeof value === "number" && Math.abs(value) < 1e-12 ? 0 : value;
    }

    function numberOr(value, fallback) {
        const n = Number(value);
        return Number.isFinite(n) ? n : fallback;
    }

    function parseTimestamp(value) {
        const n = Number(value);
        return Number.isFinite(n) ? n : 0;
    }

    function formatSeconds(seconds) {
        const cleaned = cleanNumber(seconds);
        if (Number.isInteger(cleaned)) return String(cleaned);
        return Number(cleaned).toFixed(12).replace(/0+$/, "").replace(/\.$/, "");
    }

    function formatTick(tick) {
        return cleanNumber(tick);
    }

    function isNum(value) {
        return typeof value === "number" && Number.isFinite(value);
    }

    function isSkip(value) {
        return typeof value === "string" && (value === "pal.skip" || value === "pal.disabled");
    }

    function degToRad(value) {
        return value * Math.PI / 180;
    }

    function radToDeg(value) {
        return value * 180 / Math.PI;
    }

    function showError(message) {
        Blockbench.showMessageBox({
            title: "PAL Bend Player Tools",
            message
        });
    }
})();
