// SPDX-License-Identifier: MIT
// Render the two annotated finish previews from a stage written by build_preview_scene.py.
// The same script lives in openamr-platform-hw and openamr-upperbody-hw (docs/finish/tools/).
//
//   npm install three@0.160.0        (Playwright and Chromium must be available)
//   node render_preview.mjs <stage> <node_modules/three> <output directory>
//
// Output: front_three_quarter.png and rear_three_quarter.png. Geometry is not modified; the
// colours come from scene.json (both finishes.yaml files). Labels are drawn on a 2D overlay.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const { chromium } = createRequire(import.meta.url)('playwright'); // CommonJS lookup finds a global install

const [stage, threeDir, outDir] = process.argv.slice(2);
if (!stage || !threeDir || !outDir) {
  console.error('usage: node render_preview.mjs <stage> <node_modules/three> <output directory>');
  process.exit(2);
}

const PAGE = String.raw`<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#F3F4F5}canvas{position:absolute;left:0;top:0}</style>
<script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script>
</head><body><canvas id="gl"></canvas><canvas id="ov"></canvas>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { ColladaLoader } from 'three/addons/loaders/ColladaLoader.js';
const W = 1800, H = 1300;
const scene = await (await fetch('/stage/scene.json')).json();
const gl = document.getElementById('gl'), ov = document.getElementById('ov');
gl.width = ov.width = W; gl.height = ov.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: gl, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const world = new THREE.Scene();
world.background = new THREE.Color('#F3F4F5');
world.add(new THREE.HemisphereLight(0xffffff, 0x8a8f94, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(3, 5, 2); world.add(key);
const fill = new THREE.DirectionalLight(0xffffff, 0.7); fill.position.set(-3, 2, -2); world.add(fill);
const floor = new THREE.Mesh(new THREE.CircleGeometry(4.0, 96),
  new THREE.MeshStandardMaterial({ color: '#E2E4E6', roughness: 1 }));
floor.rotation.x = -Math.PI / 2; floor.position.y = -0.098 - 0.0005; world.add(floor);
const ros = new THREE.Group(); ros.rotation.x = -Math.PI / 2; world.add(ros); // base_link, z up

const ROUGH = { matte: 0.85, satin: 0.55, gloss: 0.3, printed: 0.75, anodised: 0.45, as_delivered: 0.6 };
const mat = (hex, finish, opacity = 1) => new THREE.MeshStandardMaterial({
  color: new THREE.Color(hex), roughness: ROUGH[finish] ?? 0.6,
  metalness: finish === 'anodised' ? 0.35 : 0.05, transparent: opacity < 1, opacity,
  side: THREE.DoubleSide, depthWrite: opacity >= 1 });
const nodes = {};

// Mobile base: the model's GLB, coloured by GLB node id.
const gltf = await new GLTFLoader().loadAsync('/stage/base_visual.glb');
world.add(gltf.scene);
gltf.scene.traverse(o => {
  if (scene.base_colours[o.name]) nodes[o.name] = o;
  if (!o.isMesh) return;
  if (!o.geometry.attributes.normal) o.geometry.computeVertexNormals(); // the GLB carries no normals
  let a = o; while (a && !scene.base_colours[a.name]) a = a.parent;
  if (a && scene.base_colours[a.name].hex) o.material = mat(scene.base_colours[a.name].hex, scene.base_colours[a.name].finish);
});

// Upper body: boxes from the upper-body configuration; placeholders are translucent.
for (const b of scene.boxes) {
  const c = scene.upper_colours[b.node] || {};
  const hex = c.hex || (b.node === 'head_camera' ? '#2B2D30' : '#B9BDC1');
  const m = new THREE.Mesh(new THREE.BoxGeometry(...b.size), mat(hex, c.finish || 'as_delivered', b.placeholder ? 0.45 : 1));
  if (b.lens) {
    const g = new THREE.Group(); g.position.set(...b.lens);
    g.rotation.y = scene.pitch_down_deg * Math.PI / 180;
    m.position.set(-b.size[0] / 2, 0, 0); g.add(m); ros.add(g);
  } else { m.position.set(...b.centre); ros.add(m); }
  if (b.placeholder) {
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry), new THREE.LineBasicMaterial({ color: '#6B7075' }));
    m.add(e);
  }
  nodes[b.node] = m;
}

// OpenArm 2.0 arms at openarm_{side}_base_link, zero pose, embedded mesh materials kept.
const loader = new ColladaLoader();
const cache = {};
for (const side of ['left', 'right']) {
  const arm = new THREE.Group(); arm.position.set(...scene.arm_mounts[side]); ros.add(arm);
  nodes['arm_' + side] = arm;
  for (const item of scene.arms[side]) {
    cache[item.mesh] ??= await loader.loadAsync('/stage/' + item.mesh);
    const obj = cache[item.mesh].scene.clone(true);
    obj.rotation.set(0, 0, 0); obj.position.set(...item.xyz); obj.scale.set(...item.scale);
    obj.traverse(o => { if (o.isMesh) { o.material = (Array.isArray(o.material) ? o.material : [o.material]).map(x => { const y = x.clone(); y.side = THREE.DoubleSide; return y; }); } });
    arm.add(obj);
    if (item.link.endsWith('_base_link') && !item.link.includes('_ee_')) nodes[side + '_j1'] = obj;
  }
}
world.updateMatrixWorld(true);

// Slot cover strips: from the adapter plate up to just below the J1_A plate of each arm.
for (const s of scene.slot_strips) {
  const side = s.y > 0 ? 'left' : 'right';
  const box = new THREE.Box3().setFromObject(nodes[side + '_j1']);
  const top = box.min.y - 0.005;                       // world y equals base_link z
  const h = Math.max(0.02, top - s.z_bottom);
  const c = scene.upper_colours[s.node];
  const m = new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.002, h), mat(c.hex, c.finish));
  m.position.set(s.x, s.y + Math.sign(s.y) * 0.0005, s.z_bottom + h / 2); ros.add(m); nodes[s.node] = m;
  console.log(s.node + ': preview length ' + (h * 1000).toFixed(0) + ' mm, J1_A mesh bottom ' + ((top + 0.098 + 0.005) * 1000).toFixed(0) + ' mm above the floor');
}
world.updateMatrixWorld(true);

const cam = new THREE.PerspectiveCamera(24, W / H, 0.05, 50);
const centreOf = (name, dz = 0, dx = 0, dy = 0) => {
  const c = new THREE.Box3().setFromObject(nodes[name]).getCenter(new THREE.Vector3());
  return c.add(new THREE.Vector3(dx, dz, -dy));
};
const point = (x, y, z) => ros.localToWorld(new THREE.Vector3(x, y, z));

window.renderView = (view) => {
  const [px, py, pz] = view.eye;                         // base_link coordinates
  cam.position.copy(point(px, py, pz)); cam.up.set(0, 1, 0);
  cam.lookAt(point(...view.target)); cam.updateMatrixWorld(true);
  renderer.render(world, cam);
  const g = ov.getContext('2d'); g.clearRect(0, 0, W, H);
  g.font = '600 25px "DejaVu Sans", sans-serif'; g.textBaseline = 'middle';
  g.fillStyle = '#20252A'; g.fillText(view.title, 40, 46);
  g.font = '18px "DejaVu Sans", sans-serif'; g.fillStyle = '#4A5056';
  view.footer.forEach((t, i) => g.fillText(t, 40, H - 70 + i * 26));
  const labels = view.labels.map(l => {
    const a = centreOf(...l.at).project(cam);
    return { ...l, ax: (a.x + 1) / 2 * W, ay: (1 - a.y) / 2 * H };
  });
  // Left column for anchors left of the robot axis, right column for the others, each sorted
  // by anchor height so that leader lines do not cross.
  const mid = labels.map(l => l.ax).sort((a, b) => a - b)[Math.floor(labels.length / 2)];
  labels.forEach(l => { l.side = l.ax < mid ? 'L' : 'R'; });
  for (const side of ['L', 'R']) {
    const list = labels.filter(l => l.side === side).sort((a, b) => a.ay - b.ay);
    const n = list.length, top = 120, step = Math.min(118, (H - 260) / Math.max(1, n - 1));
    list.forEach((l, i) => {
      const ty = top + i * step, tx = side === 'L' ? 40 : W - 470;
      g.strokeStyle = '#6B7177'; g.lineWidth = 1.6; g.beginPath();
      const ex = side === 'L' ? tx + 430 : tx - 12;
      g.moveTo(ex, ty); g.lineTo(l.ax, l.ay); g.stroke();
      g.fillStyle = '#20252A'; g.beginPath(); g.arc(l.ax, l.ay, 4.5, 0, 2 * Math.PI); g.fill();
      if (l.tag) { g.fillStyle = l.tagColour || '#20252A'; g.fillRect(tx, ty - 15, 54, 30);
        g.fillStyle = '#FFFFFF'; g.font = '700 18px "DejaVu Sans", sans-serif'; g.fillText(l.tag, tx + 8, ty); }
      g.fillStyle = '#20252A'; g.font = '600 18px "DejaVu Sans", sans-serif';
      const x0 = tx + (l.tag ? 64 : 0);
      g.fillText(l.text[0], x0, ty - (l.text.length > 1 ? 11 : 0));
      g.font = '16px "DejaVu Sans", sans-serif'; g.fillStyle = '#4A5056';
      l.text.slice(1).forEach((t, k) => g.fillText(t, x0, ty + 11 + k * 21));
    });
  }
  const out = document.createElement('canvas'); out.width = W; out.height = H;
  const o = out.getContext('2d'); o.drawImage(gl, 0, 0); o.drawImage(ov, 0, 0);
  return out.toDataURL('image/png');
};
window.ready = true;
</script></body></html>`;

const FOOTER = [
  'Colours: docs/finish/finishes.yaml of openamr-platform-hw and openamr-upperbody-hw; sRGB screen values of the RAL references, a physical sample governs.',
  'Geometry: openamr-platform-sw base GLB, upper-body configuration values and OpenArm 2.0 meshes, unchanged. Translucent: placeholder, outline not established.',
];
const VIEWS = {
  front_three_quarter: {
    title: 'OpenAMRobot 2.0 finish preview, front three-quarter (lift 0, bp000, hp25)',
    eye: [3.05, 2.1, 1.45], target: [0.03, 0.0, 0.44], footer: FOOTER,
    labels: [
      { side: 'L', at: ['head_camera'], text: ['Head camera ZED Mini: as delivered', 'pitch bracket black RAL 9005 (not modelled, verify)'] },
      { side: 'L', at: ['arm_left', -0.12], tag: 'I3', tagColour: '#F44611', text: ['OpenArm printed inserts: RAL 2004', 'orange; parts not identified, not shown'] },
      { side: 'L', at: ['slot_cover_left'], tag: 'I1', tagColour: '#3F888F', text: ['Slot cover strip, left face: RAL 5018', 'push-in, front-most slot (verify)'] },
      { side: 'L', at: ['lift_column', 0.1], text: ['Lift column DOLD Hexalift V4: as delivered', 'placeholder shape, no paint or inserts'] },
      { side: 'L', at: ['cover', 0, 0.2, 0.15], text: ['Upper cover and flanges: RAL 7016 graphite', 'matte powder; base plate footprint masked'] },
      { side: 'L', at: ['camera_mount'], text: ['Printed mounts: black PETG, RAL 9005', 'camera, ToF and MB7060 mounts'] },
      { side: 'L', at: ['front_panel', 0.02], text: ['Front panel: RAL 7035, matte powder', 'S1 E-stop red on yellow, keep-out K1'] },
      { side: 'R', at: ['arm_profile', 0.12], text: ['Arm profile HFS6-60120: dark anodised,', 'RAL 7016 target; never painted (verify)'] },
      { side: 'R', at: ['adapter_plate'], text: ['Adapter plate: black anodised (verify)', '6082-T6, 360 x 100 x 10 mm'] },
      { side: 'R', at: ['lift_base_plate'], text: ['Lift base plate: black anodised (verify)', 'outline pending, placeholder'] },
      { side: 'R', at: ['side_panel_left'], text: ['Side panels: RAL 7035 light grey', 'matte powder, 0.8 mm steel'] },
      { side: 'R', at: ['ultrasonic_front_right'], text: ['Sensors, LiDAR, wheels, castors: as delivered', 'windows and lenses never covered'] },
    ],
  },
  rear_three_quarter: {
    title: 'OpenAMRobot 2.0 finish preview, rear three-quarter (lift 0, bp000, hp25)',
    eye: [-3.05, -2.1, 1.45], target: [0.03, 0.0, 0.44], footer: FOOTER,
    labels: [
      { side: 'L', at: ['arm_profile', 0.12, -0.06], text: ['Rear slots: rear upright T-nuts', 'no strips; front slots kept free'] },
      { side: 'L', at: ['arm_right', -0.12], tag: 'I3', tagColour: '#F44611', text: ['OpenArm printed inserts: RAL 2004', 'orange; parts not identified, not shown'] },
      { side: 'L', at: ['lift_column', 0.1], text: ['Lift column: as delivered', 'telescoping surfaces never covered'] },
      { side: 'L', at: ['cover', 0, -0.2, -0.15], text: ['Upper cover: RAL 7016 graphite, matte', 'cooling openings and scan band open'] },
      { side: 'L', at: ['rear_panel', 0.02], text: ['Rear panel: RAL 7035, matte powder', 'RESET position to confirm, keep-out K1'] },
      { side: 'L', at: ['tof_mount_rear'], text: ['TF-Luna and MB7060 mounts: black PETG', 'lenses and transducers never covered'] },
      { side: 'R', at: ['head_camera'], text: ['Head camera: as delivered', 'lenses never covered'] },
      { side: 'R', at: ['slot_cover_right'], tag: 'I2', tagColour: '#3F888F', text: ['Slot cover strip, right face: RAL 5018', 'push-in, front-most slot (verify)'] },
      { side: 'R', at: ['adapter_plate'], text: ['Adapter plate and lift base plate:', 'black anodised (verify)'] },
      { side: 'R', at: ['side_panel_right'], text: ['Side panels: RAL 7035 light grey', 'matte powder'] },
      { side: 'R', at: ['hub_motor_wheel_right'], text: ['Hub motors and castors: as delivered', 'no paint, no bumper or edge strips'] },
    ],
  },
};

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.glb': 'model/gltf-binary', '.dae': 'model/vnd.collada+xml' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let file = null;
  if (url === '/') { res.writeHead(200, { 'content-type': 'text/html' }); return res.end(PAGE); }
  if (url.startsWith('/stage/')) file = path.join(stage, url.slice(7));
  if (url.startsWith('/three/')) file = path.join(threeDir, url.slice(7));
  if (!file || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
}).listen(0, '127.0.0.1');
await new Promise(r => server.once('listening', r));
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1800, height: 1300 } });
page.on('console', m => console.log('page:', m.text()));
page.on('pageerror', e => console.log('page error:', e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/`);
await page.waitForFunction('window.ready === true', null, { timeout: 600000 });
fs.mkdirSync(outDir, { recursive: true });
for (const [name, view] of Object.entries(VIEWS)) {
  const data = await page.evaluate(v => window.renderView(v), view);
  fs.writeFileSync(path.join(outDir, `${name}.png`), Buffer.from(data.split(',')[1], 'base64'));
  console.log(`wrote ${path.join(outDir, name + '.png')}`);
}
await browser.close();
server.close();
