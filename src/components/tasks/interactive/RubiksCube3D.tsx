"use client";

import { useRef, useState, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

/**
 * A 3×3×3 cube built from 27 unit cubes. Outer-facing faces are painted red;
 * the rest are unpainted (cream/beige). Defaults to slow auto-rotation; the
 * teacher can grab and rotate it; on idle the auto-rotation resumes — UNLESS
 * the teacher has clicked the stop switch below the cube, in which case the
 * cube stays frozen but is still draggable.
 */

const PAINTED_COLOR = "#ef4444"; // pnp-red
const UNPAINTED_COLOR = "#f8eddb"; // soft cream — unpainted interior wood feel
const N = 3; // cube dimension

interface Props {
  /** Optional width in pixels. If omitted, the canvas fills its container
   *  (responsive). Useful for callers that want to clamp the size. */
  width?: number;
  /** Background color behind the cube. Set to "transparent" by default. */
  background?: string;
}

export default function RubiksCube3D({ width, background = "transparent" }: Props) {
  // Master switch for auto-rotation. When OFF, the cube is fully manual —
  // dragging still works but it never spins on its own.
  const [autoRotateEnabled, setAutoRotateEnabled] = useState(true);

  // The container is split into the canvas (fills available height minus the
  // toggle's reserved space) and a button row beneath it.
  const containerStyle: React.CSSProperties = width
    ? { width, height: width, touchAction: "none" }
    : { width: "100%", height: "100%", touchAction: "none" };

  return (
    <div className="flex flex-col" style={containerStyle}>
      {/* The 3D canvas itself — fills the remaining height of the container. */}
      <div className="min-h-0 flex-1">
        <Canvas
          // Camera pulled well back so the cube reads small with margin on
          // every side, regardless of container ratio or rotation angle.
          camera={{ position: [16, 12.6, 19.5], fov: 12 }}
          gl={{ alpha: true, antialias: true }}
          style={{ background }}
        >
          <ambientLight intensity={0.55} />
          <directionalLight position={[5, 8, 5]} intensity={0.9} />
          <directionalLight position={[-5, -3, -2]} intensity={0.25} />

          <CubeGroup autoRotateEnabled={autoRotateEnabled} />

          <OrbitControls
            enablePan={false}
            enableZoom={false}
            enableDamping
            dampingFactor={0.08}
            rotateSpeed={0.7}
          />
        </Canvas>
      </div>

      {/* Stop switch — sits beneath the cube. Same visual vocabulary as the
          rest of the app's small toggles. */}
      <div className="flex shrink-0 justify-center pt-2 pb-1">
        <button
          type="button"
          onClick={() => setAutoRotateEnabled((v) => !v)}
          aria-pressed={autoRotateEnabled}
          className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
            autoRotateEnabled
              ? "border-current bg-current/10 text-current hover:bg-current/20"
              : "border-current/40 text-current/70 hover:bg-current/10"
          }`}
          title={
            autoRotateEnabled
              ? "Stop the cube from spinning (you can still drag it)"
              : "Restart slow auto-rotation"
          }
        >
          {autoRotateEnabled ? (
            <>
              <span className="inline-block h-2.5 w-2.5 rounded-sm bg-current" aria-hidden="true" />
              <span>Stop spinning</span>
            </>
          ) : (
            <>
              <span
                className="inline-block h-0 w-0 border-y-[5px] border-l-[8px] border-y-transparent border-l-current"
                aria-hidden="true"
              />
              <span>Start spinning</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

function CubeGroup({ autoRotateEnabled }: { autoRotateEnabled: boolean }) {
  const groupRef = useRef<THREE.Group>(null);
  // Local "I'm being dragged" suspension. Independent of the master switch so
  // a drag temporarily pauses spin even when auto-rotation is on, and the
  // 2.5-second idle timer hands control back to auto-rotation.
  const [draggingPaused, setDraggingPaused] = useState(false);
  const lastInteractionRef = useRef<number>(performance.now());

  // Sync OrbitControls drags into our pause/resume state. We listen on the
  // canvas's pointer events because drei's OrbitControls fires its own
  // events but we don't hold a ref to the controls instance here.
  const { gl } = useThree();
  useEffect(() => {
    const dom = gl.domElement;
    const onDown = () => {
      setDraggingPaused(true);
      lastInteractionRef.current = performance.now();
    };
    const onUp = () => {
      lastInteractionRef.current = performance.now();
    };
    dom.addEventListener("pointerdown", onDown);
    dom.addEventListener("pointerup", onUp);
    dom.addEventListener("pointercancel", onUp);
    return () => {
      dom.removeEventListener("pointerdown", onDown);
      dom.removeEventListener("pointerup", onUp);
      dom.removeEventListener("pointercancel", onUp);
    };
  }, [gl]);

  // Per frame: spin only when both (a) auto-rotation is ENABLED and (b) the
  // drag pause has expired. Drag pause auto-clears 2.5s after last interaction.
  useFrame((_, delta) => {
    if (!groupRef.current) return;
    const now = performance.now();
    const idleFor = now - lastInteractionRef.current;
    if (draggingPaused && idleFor > 2500) {
      setDraggingPaused(false);
    }
    if (autoRotateEnabled && !draggingPaused) {
      groupRef.current.rotation.y += delta * 0.35;
      groupRef.current.rotation.x = Math.sin(now * 0.0002) * 0.15;
    }
  });

  // Build the 27 cubelets. Spacing slightly less than 1 so we get a visible
  // gap between cubelets — reads more like a Rubik's cube than a solid block.
  const spacing = 1.06;
  const cubelets = [];
  const half = (N - 1) / 2;
  for (let x = 0; x < N; x++) {
    for (let y = 0; y < N; y++) {
      for (let z = 0; z < N; z++) {
        const px = (x - half) * spacing;
        const py = (y - half) * spacing;
        const pz = (z - half) * spacing;
        cubelets.push(
          <Cubelet
            key={`${x}-${y}-${z}`}
            position={[px, py, pz]}
            painted={[
              x === N - 1, // +x face
              x === 0,     // -x face
              y === N - 1, // +y face
              y === 0,     // -y face
              z === N - 1, // +z face
              z === 0,     // -z face
            ]}
          />
        );
      }
    }
  }

  return <group ref={groupRef}>{cubelets}</group>;
}

function Cubelet({
  position,
  painted,
}: {
  position: [number, number, number];
  painted: [boolean, boolean, boolean, boolean, boolean, boolean];
}) {
  return (
    <mesh position={position} castShadow receiveShadow>
      <boxGeometry args={[1, 1, 1]} />
      {painted.map((isOuter, i) => (
        <meshStandardMaterial
          key={i}
          attach={`material-${i}`}
          color={isOuter ? PAINTED_COLOR : UNPAINTED_COLOR}
          roughness={0.55}
          metalness={0}
        />
      ))}
      {/* Black wireframe edges so the 3×3 grid reads clearly */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(1, 1, 1)]} />
        <lineBasicMaterial color="#1a1f3d" linewidth={1} />
      </lineSegments>
    </mesh>
  );
}
