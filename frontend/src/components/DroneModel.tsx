import React, { useRef, useMemo } from "react";
import { useFrame, useGraph } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { SkeletonUtils } from "three-stdlib";

interface DroneModelProps {
  position?: [number, number, number];
  rotationOffset?: number;
  isHovered?: boolean;
}

export const DroneModel = ({ position = [0, 0, 0], rotationOffset = 0, isHovered = false }: DroneModelProps) => {
  const { scene } = useGLTF("/models/drone/scene.gltf");

  // Create a distinct clone for each instance using SkeletonUtils
  const clone = useMemo(() => SkeletonUtils.clone(scene), [scene]);
  const { nodes, materials } = useGraph(clone);

  const modelRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!modelRef.current) return;

    let targetRotationY = rotationOffset;
    let targetRotationX = 0;

    if (isHovered) {
      // Mouse position in range [-1, 1]
      const { x, y } = state.pointer;
      // More aggressive follow and tilt
      targetRotationY = x * 0.8 + rotationOffset;
      targetRotationX = -y * 0.5;
    }

    // Smooth interpolation (Lerp) - slightly faster for responsiveness
    modelRef.current.rotation.y = THREE.MathUtils.lerp(
      modelRef.current.rotation.y,
      targetRotationY,
      0.08
    );
    modelRef.current.rotation.x = THREE.MathUtils.lerp(
      modelRef.current.rotation.x,
      targetRotationX,
      0.08
    );

    // Add a slight hover float
    modelRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2 + rotationOffset) * 0.2;
  });

  return (
    <primitive
      ref={modelRef}
      object={clone}
      scale={4.5}
      position={position}
    />
  );
};

useGLTF.preload("/models/drone/scene.gltf");
