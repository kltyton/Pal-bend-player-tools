const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');

function loadTools(filename) {
    const context = {Plugin: {register() {}}, console};
    vm.createContext(context);
    const source = fs.readFileSync(filename, 'utf8').replace(/\}\)\(\);\s*$/, `
        globalThis.tools = {getHierarchyMetadataRig, compileAnimationsFromProject,
            jsonElementToBlockbenchKey, blockbenchKeyframesToTrack, mirrorKeyPayload,
            sampleTrackVector, getBakeTimes, findBakeEasing, mirrorPoseVector,
            detectRigFromEntries, exportBoneTracksForInterop, importPalTracksForInterop,
            PLAYER_MODEL_TEXTURE_DATA_URL};
    })();`);
    vm.runInContext(source, context, {filename});
    return context.tools;
}

const plugin = process.argv[2] || path.join(__dirname, '..', 'pal_bend_player_tools.js');
const tools = loadTools(plugin);
const plain = value => JSON.parse(JSON.stringify(value));

test('animation-local model and parents override shared root defaults', () => {
    const input = {parents: {head: 'body'}, model: {custom: {pivot: [1, 2, 3]}},
        animations: {wave: {parents: {head: 'custom'}, model: {custom: {pivot: [4, 5, 6]}}}}};
    const result = tools.getHierarchyMetadataRig(input);
    assert.equal(result.parents.head, 'custom');
    assert.deepEqual(plain(result.pivots.custom), [4, 5, 6]);
});

test('Blender loop return time and PAL metadata survive editable animation export', () => {
    const animation = {name: 'wave', length: 2, loop: 'loop', animators: {},
        pal_bend_animation_metadata: {loopTick: 0.5, player_animation_library: {name: 'Wave', author: 'Fixture', iconData: 'aWNvbg=='}}};
    const result = tools.compileAnimationsFromProject([animation]).animations.wave;
    assert.equal(result.loopTick, 0.5);
    assert.deepEqual(plain(result.player_animation_library), animation.pal_bend_animation_metadata.player_animation_library);
});

test('Blender per-axis bezier handles retain value offsets and seconds on round trip', () => {
    const input = {vector: [45, 0, 90], easingX: 'bezier', easingArgsX: [0.2, -0.3, 0.8, 1.4], easingY: 'linear', easingZ: 'easeInSine'};
    const key = tools.jsonElementToBlockbenchKey(input, 'rotation');
    const result = tools.blockbenchKeyframesToTrack([{time: 0, data_points: key.dataPoints,
        easing: key.easing, pal_bend_easing: key.palEasing}], 'rotation')['0'];
    assert.deepEqual(plain(result.easingArgsX), input.easingArgsX);
    assert.equal(result.easingX, 'bezier');
    assert.equal(result.easingZ, 'easeInSine');
});

test('mirroring negates only bezier value handles on the mirrored axes', () => {
    const input = {vector: [10, 20, 30], easing: 'bezier', easingArgs: [-2, -0.1, 3, 0.2]};
    const result = tools.mirrorKeyPayload(input, 'rotation');
    assert.deepEqual(plain(result.easingArgsX), [2, -0.1, -3, 0.2]);
    assert.deepEqual(plain(result.easingArgsY), [2, -0.1, -3, 0.2]);
    assert.deepEqual(plain(result.easingArgsZ), input.easingArgs);
    const restored = tools.mirrorKeyPayload(result, 'rotation');
    assert.deepEqual(plain(restored.vector), input.vector);
    for (const axis of ['X', 'Y', 'Z']) assert.deepEqual(plain(restored['easingArgs' + axis]), input.easingArgs);
});

test('sampling uses previous outgoing and next incoming handles independently per axis', () => {
    const track = {
        0: {vector: [0, 0, 0], easingX: 'bezier', easingArgsX: [0, 0, 8, 1/3]},
        1: {vector: [10, 10, 10], easingX: 'bezier', easingArgsX: [-1, -1/3, 0, 0], easingY: 'linear', easingZ: 'easeInQuad'}
    };
    const sampled = plain(tools.sampleTrackVector(track, 'position', 0.5, [0, 0, 0]));
    assert.ok(Math.abs(sampled[0] - 7.625) < 0.0001);
    assert.equal(sampled[1], 5);
    assert.equal(sampled[2], 2.5);
});

test('hierarchy changes sample curved inputs and do not copy invalid handles into other channels', () => {
    const bones = {head: {rotation: {0: {vector: [0, 0, 0]}, 1: {vector: [20, 0, 0], easingX: 'easeInQuad'}}}};
    assert.ok(tools.getBakeTimes(bones, 'head', []).length >= 61);
    assert.deepEqual(plain(tools.findBakeEasing(bones, 'head', [], 1)), {easing: 'linear'});
});

test('Blender pal.disabled keys leave each axis on its own timeline', () => {
    const track = {
        0: {vector: [0, 0, 0], easingX: 'linear', easingY: 'linear', easingZ: 'linear'},
        0.5: {vector: ['pal.disabled', 10, 'pal.disabled'], easingY: 'linear'},
        1: {vector: [20, 'pal.disabled', 30], easingX: 'linear', easingZ: 'linear'}
    };
    assert.deepEqual(plain(tools.sampleTrackVector(track, 'rotation', 0.5, [0, 0, 0])), [10, 10, 15]);
});

test('Pose mirroring flips Y/Z rotations and X positions across the sagittal plane', () => {
    assert.deepEqual(plain(tools.mirrorPoseVector([45, 20, -15], 'rotation')), [45, -20, 15]);
    assert.deepEqual(plain(tools.mirrorPoseVector([6, 12, -3], 'position')), [-6, 12, -3]);
    assert.deepEqual(plain(tools.mirrorPoseVector([1.2, 0.9, 1.1], 'scale')), [1.2, 0.9, 1.1]);
});

test('Interop export/import round-trips 3-axis MoreRotation bends in strict AnimCue vector form', () => {
    const exported = tools.exportBoneTracksForInterop('wave', {
        right_arm: {rotation: {0: [0, 0, 0], 0.5: [60, 0, -10]}},
        right_arm_bend: {rotation: {0: [0, 0, 0], 0.5: [42, 18, -12]}}
    }, {preset: 'player', length: 1, animcueStrict: true});
    assert.equal(exported.needsMoreRotation, true);
    assert.equal(exported.bones.right_arm_bend, undefined);
    assert.deepEqual(plain(exported.bones.right_arm.rotation['0.5']), [-60, 0, -10]);
    assert.deepEqual(plain(exported.bones.right_arm.bend['0.5']), [-42, -18, -12]);

    const restored = tools.importPalTracksForInterop({
        format_version: '1.8.0',
        animations: {wave: {animation_length: 1, bones: exported.bones}}
    }, {targetPreset: 'player'});
    const bend05 = restored.animations.wave.bones.right_arm_bend.rotation['0.5'];
    const bendVec = Array.isArray(bend05) ? bend05 : (bend05.post || bend05.vector);
    assert.deepEqual(plain(bendVec), [42, 18, -12]);
});

test('Bundled player_model.geo.png data URL is a valid non-truncated PNG', () => {
    const prefix = 'data:image/png;base64,';
    assert.ok(tools.PLAYER_MODEL_TEXTURE_DATA_URL.startsWith(prefix));
    const buf = Buffer.from(tools.PLAYER_MODEL_TEXTURE_DATA_URL.slice(prefix.length), 'base64');
    assert.ok(buf.length > 2000);
    assert.equal(buf.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
    assert.equal(buf.subarray(buf.length - 8, buf.length - 4).toString('ascii'), 'IEND');
});
