#!/usr/bin/env python3
"""
Dispatches 15 strictly disjoint computational engine tasks to Google Jules REST API.
Guarantees zero file intersection across concurrent pull requests.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://jules.googleapis.com/v1alpha"
DEFAULT_SOURCE = "sources/github/Evgenii-Zinner/Sting"
DEFAULT_BRANCH = "main"


def get_api_key() -> str:
    if os.environ.get("JULES_API_KEY"):
        return os.environ["JULES_API_KEY"].strip()
    key_paths = [
        os.path.join(os.path.dirname(__file__), ".jules_key"),
        os.path.join(os.path.dirname(__file__), "..", ".jules_key"),
    ]
    for kp in key_paths:
        if os.path.exists(kp):
            with open(kp, "r") as f:
                k = f.read().strip()
                if k:
                    return k
    sys.stderr.write("Error: JULES_API_KEY environment variable or tools/.jules_key file not found.\n")
    sys.exit(1)

TASKS = [
    {
        "id": 1,
        "title": "feat: Continuous Bilinear Scalar Field Sampler",
        "role": "Mathematics Engineer",
        "skill": "skills/mathematics_engineer.json",
        "target_files": ["lib/engine/math/scalar_field_sampler.dart"],
        "test_files": ["test/engine/math/scalar_field_sampler_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Mathematics Engineer (see skills/mathematics_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation continuous 2D scalar field sampling with bilinear interpolation.
1. Create lib/engine/math/scalar_field_sampler.dart:
   - Provide high-performance static methods or class ScalarFieldSampler.
   - sampleBilinear(Float32List grid, int cols, int rows, double x, double y, {bool wrap = false, double defaultValue = 0.0}):
     Takes continuous float coordinates (x, y) relative to discrete grid dimensions.
     Calculates the 4 bounding cell indices and fractional offsets (tx, ty).
     Performs bilinear interpolation: lerp(lerp(c00, c10, tx), lerp(c01, c11, tx), ty).
     Supports edge clamping, zero-padding, or toroidal coordinate wrapping.
   - Zero heap allocations per sample call.
2. Create test/engine/math/scalar_field_sampler_test.dart:
   - 100% test coverage verifying exact corner hits, midpoint interpolation, out-of-bounds clamping, and wrapping.
Verify:
- flutter test test/engine/math/scalar_field_sampler_test.dart passes cleanly.
""",
    },
    {
        "id": 2,
        "title": "feat: Continuous Field Numerical Gradient Kernel",
        "role": "Mathematics Engineer",
        "skill": "skills/mathematics_engineer.json",
        "target_files": ["lib/engine/math/field_gradient.dart"],
        "test_files": ["test/engine/math/field_gradient_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Mathematics Engineer (see skills/mathematics_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation numerical gradient calculation from continuous 2D scalar fields.
1. Create lib/engine/math/field_gradient.dart:
   - Provide static function or class FieldGradient.
   - computeGradient(Float32List grid, int cols, int rows, double x, double y, {double epsilon = 1.0, bool normalize = false}):
     Computes central finite differences:
       dx = (sample(x + epsilon, y) - sample(x - epsilon, y)) / (2 * epsilon)
       dy = (sample(x, y + epsilon) - sample(x, y - epsilon)) / (2 * epsilon)
     Returns a Dart 3 record: (double dx, double dy, double magnitude).
   - Zero heap allocations.
2. Create test/engine/math/field_gradient_test.dart:
   - 100% test coverage testing linear slopes, saddle points, radial peaks, and flat regions.
Verify:
- flutter test test/engine/math/field_gradient_test.dart passes cleanly.
""",
    },
    {
        "id": 3,
        "title": "feat: Point-to-Grid Gaussian and Bilinear Splatting Kernel",
        "role": "Mathematics Engineer",
        "skill": "skills/mathematics_engineer.json",
        "target_files": ["lib/engine/math/field_splatting.dart"],
        "test_files": ["test/engine/math/field_splatting_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Mathematics Engineer (see skills/mathematics_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation continuous point deposition / splatting onto discrete 2D float grids.
1. Create lib/engine/math/field_splatting.dart:
   - Provide FieldSplatting routines:
   - splatBilinear(Float32List grid, int cols, int rows, double x, double y, double amount, [double maxCap]):
     Distributes amount across the 4 surrounding discrete cells inversely proportional to distance.
   - splatRadialGaussian(Float32List grid, int cols, int rows, double centerX, double centerY, double radius, double peakValue, [double maxCap]):
     Applies Gaussian or quadratic radial falloff to cells within the radius.
   - Bounds-checked, handles edge clipping safely. Zero allocations.
2. Create test/engine/math/field_splatting_test.dart:
   - 100% test coverage verifying energy conservation, radial bounds clipping, and cell capping.
Verify:
- flutter test test/engine/math/field_splatting_test.dart passes cleanly.
""",
    },
    {
        "id": 4,
        "title": "feat: 2D Vector Flow Field Component and Storage",
        "role": "Simulation Engineer",
        "skill": "skills/simulation_engineer.json",
        "target_files": ["lib/engine/components/vector_field_2d.dart"],
        "test_files": ["test/engine/components/vector_field_2d_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Simulation Engineer (see skills/simulation_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation 2D Vector Flow Field component.
1. Create lib/engine/components/vector_field_2d.dart:
   - Flat Float32List extension type VectorField2D.
   - Memory layout:
     - Index 0: columns
     - Index 1: rows
     - Index 2: cellSize
     - Index 3..: interleaved vx, vy pairs (size = 3 + 2 * cols * rows).
   - Getters/setters: getVx(int col, int row), getVy(int col, int row), setVector(int col, int row, double vx, double vy).
   - getVector(int col, int row) returning Dart 3 record (double vx, double vy).
   - sampleBilinearVector(double worldX, double worldY) returning interpolated (double vx, double vy).
   - Zero heap allocations.
2. Create test/engine/components/vector_field_2d_test.dart:
   - 100% test coverage verifying dimensions, layout indexing, vector accessors, and bilinear vector sampling.
Verify:
- flutter test test/engine/components/vector_field_2d_test.dart passes cleanly.
""",
    },
    {
        "id": 5,
        "title": "feat: Eikonal Wavefront Potential Field Solver",
        "role": "AI & Pathfinding Engineer",
        "skill": "skills/ai_pathfinding_engineer.json",
        "target_files": ["lib/engine/ai/potential_field_solver.dart"],
        "test_files": ["test/engine/ai/potential_field_solver_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: AI & Pathfinding Engineer (see skills/ai_pathfinding_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation Eikonal / Wavefront Potential Field Solver.
1. Create lib/engine/ai/potential_field_solver.dart:
   - Class PotentialFieldSolver with pre-allocated scratch ring-buffers (Int32List queue).
   - solveWavefront(Float32List potentialGrid, Uint8List costOrObstacleGrid, int cols, int rows, Int32List goalCells):
     Initializes goal cells to 0.0, non-goals to infinity.
     Propagates wave outward using 8-directional neighbor cost accumulation.
     Writes resulting distance/potential surface into potentialGrid.
   - deriveFlowVectors(Float32List potentialGrid, Float32List outVectorGrid, int cols, int rows):
     Computes normalized downhill gradient direction for each cell into outVectorGrid.
   - Zero runtime allocations per solve call.
2. Create test/engine/ai/potential_field_solver_test.dart:
   - 100% test coverage verifying obstacle avoidance, multi-goal wavefront propagation, and correct downhill flow vectors.
Verify:
- flutter test test/engine/ai/potential_field_solver_test.dart passes cleanly.
""",
    },
    {
        "id": 6,
        "title": "feat: Bit-Packed Cellular Automata Grid Component",
        "role": "Simulation Engineer",
        "skill": "skills/simulation_engineer.json",
        "target_files": ["lib/engine/components/cellular_grid.dart"],
        "test_files": ["test/engine/components/cellular_grid_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Simulation Engineer (see skills/simulation_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation Cellular Automata Grid component.
1. Create lib/engine/components/cellular_grid.dart:
   - Double-buffered flat Uint8List extension type CellularGrid.
   - Header (first 8 bytes via ByteData/Uint8List):
     - cols (Uint16), rows (Uint16), activeBuffer (Uint8: 0 or 1), cellSize (Uint8), reserved (Uint16).
     - Followed by Buffer A (cols * rows bytes) and Buffer B (cols * rows bytes).
   - Methods:
     - getState(int col, int row), setState(int col, int row, int state).
     - getNextBufferState(int col, int row), setNextBufferState(int col, int row, int state).
     - swapBuffers(): flips activeBuffer between 0 and 1 without reallocating.
     - countNeighbors(int col, int row, int targetState, {bool moore = true}): counts matching neighbor states.
2. Create test/engine/components/cellular_grid_test.dart:
   - 100% test coverage verifying buffer flipping, state read/write, Moore vs Von Neumann neighbor counts, and boundary checks.
Verify:
- flutter test test/engine/components/cellular_grid_test.dart passes cleanly.
""",
    },
    {
        "id": 7,
        "title": "feat: Cellular Automata Step Simulation System and LUT Kernel",
        "role": "Simulation Engineer",
        "skill": "skills/simulation_engineer.json",
        "target_files": ["lib/engine/systems/cellular_simulation_system.dart"],
        "test_files": ["test/engine/systems/cellular_simulation_system_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Simulation Engineer (see skills/simulation_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement Cellular Automata Simulation System with Lookup Table (LUT) support.
1. Create lib/engine/systems/cellular_simulation_system.dart:
   - CellularSimulationSystem executing rule steps on cellular grids.
   - Supports Lookup Table (Uint8List transitionLUT) or integer rule evaluation:
     - E.g. Conway's Life LUT or generic phase-transition rule (empty -> liquid -> solid).
   - stepGrid(Uint8List gridData, Uint8List lut, {bool moore = true}):
     Iterates all internal cells, counts active neighbors, looks up new state in LUT, writes to inactive buffer, and swaps buffers.
   - Zero per-frame allocations.
2. Create test/engine/systems/cellular_simulation_system_test.dart:
   - 100% test coverage testing Game of Life blinkers/gliders and 3-state solidification transitions.
Verify:
- flutter test test/engine/systems/cellular_simulation_system_test.dart passes cleanly.
""",
    },
    {
        "id": 8,
        "title": "feat: Multi-Channel Coupled Grid Diffusion Component",
        "role": "Simulation Engineer",
        "skill": "skills/simulation_engineer.json",
        "target_files": ["lib/engine/components/multi_channel_diffusion.dart"],
        "test_files": ["test/engine/components/multi_channel_diffusion_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Simulation Engineer (see skills/simulation_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation Multi-Channel Grid Diffusion component.
1. Create lib/engine/components/multi_channel_diffusion.dart:
   - Extension type MultiChannelDiffusion over Float32List.
   - Supports N interleaved floating point channels per cell (e.g. Channel 0: Heat, Channel 1: Vapor/Scent, Channel 2: Density).
   - Double-buffered: Buffer A and Buffer B.
   - Header:
     - Index 0: columns
     - Index 1: rows
     - Index 2: channelCount
     - Index 3: activeBuffer (0.0 or 1.0)
     - Index 4..4+N: per-channel diffusion rates.
     - Index 4+N..: Buffer A (cols * rows * N floats), followed by Buffer B (cols * rows * N floats).
   - Accessors: getValue(int col, int row, int channel), setValue(int col, int row, int channel, double val), swapBuffers().
2. Create test/engine/components/multi_channel_diffusion_test.dart:
   - 100% test coverage verifying channel offsets, multi-channel reads/writes, buffer swaps, and bounds validation.
Verify:
- flutter test test/engine/components/multi_channel_diffusion_test.dart passes cleanly.
""",
    },
    {
        "id": 9,
        "title": "feat: Multi-Channel Diffusion and Advection System",
        "role": "Simulation Engineer",
        "skill": "skills/simulation_engineer.json",
        "target_files": ["lib/engine/systems/multi_channel_diffusion_system.dart"],
        "test_files": ["test/engine/systems/multi_channel_diffusion_system_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Simulation Engineer (see skills/simulation_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement Multi-Channel Diffusion & Advection System.
1. Create lib/engine/systems/multi_channel_diffusion_system.dart:
   - MultiChannelDiffusionSystem executing 5-point discrete 2D Laplacian diffusion across each channel of a multi-channel grid.
   - Supports decay rates per channel (e.g. dissipation rate).
   - Updates target buffer from active buffer and swaps buffers.
   - Zero heap allocations during update loop.
2. Create test/engine/systems/multi_channel_diffusion_system_test.dart:
   - 100% test coverage verifying independent diffusion rates per channel, conservation of total mass/heat, and boundary reflection/absorption.
Verify:
- flutter test test/engine/systems/multi_channel_diffusion_system_test.dart passes cleanly.
""",
    },
    {
        "id": 10,
        "title": "feat: Compound Hierarchical Bounding Box System",
        "role": "Physics Engineer",
        "skill": "skills/physics_engineer.json",
        "target_files": [
            "lib/engine/components/compound_bounding_box.dart",
            "lib/engine/systems/compound_bounding_box_system.dart",
        ],
        "test_files": ["test/engine/systems/compound_bounding_box_system_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Physics Engineer (see skills/physics_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target files and test file.

Task: Implement Compound Bounding Box component and hierarchical bounds aggregator system.
1. Create lib/engine/components/compound_bounding_box.dart:
   - Extension type CompoundBoundingBox over Float32List (minX, minY, maxX, maxY, childCount, dirtyFlag).
2. Create lib/engine/systems/compound_bounding_box_system.dart:
   - Traverses entity parent-child relationships (using Parent, Position, BoundingBox).
   - Unions the world-space bounding boxes of all attached children into the root entity's CompoundBoundingBox.
   - Updates root entity's outer BoundingBox for broadphase spatial queries.
   - Zero per-frame allocations.
3. Create test/engine/systems/compound_bounding_box_system_test.dart:
   - 100% test coverage verifying bounds expansion as child entities move, rotate, or are attached/detached.
Verify:
- flutter test test/engine/systems/compound_bounding_box_system_test.dart passes cleanly.
""",
    },
    {
        "id": 11,
        "title": "feat: Compound Rigid Mass and Inertia Calculator",
        "role": "Physics Engineer",
        "skill": "skills/physics_engineer.json",
        "target_files": ["lib/engine/math/compound_mass_calculator.dart"],
        "test_files": ["test/engine/math/compound_mass_calculator_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Physics Engineer (see skills/physics_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement zero-allocation Compound Rigid Mass & Inertia Calculator.
1. Create lib/engine/math/compound_mass_calculator.dart:
   - Static methods to calculate center of mass and moment of inertia for multi-part assemblies:
   - calculateCenterOfMass(Float32List masses, Float32List positionsX, Float32List positionsY, int count):
     Returns Dart 3 record (double totalMass, double comX, double comY).
   - calculateMomentOfInertia2D(Float32List masses, Float32List localX, Float32List localY, Float32List localInertias, int count, double comX, double comY):
     Applies Parallel Axis Theorem: I = sum(I_i + m_i * distanceSq).
     Returns double totalInertia.
   - Zero heap allocations.
2. Create test/engine/math/compound_mass_calculator_test.dart:
   - 100% test coverage verifying analytical balance for asymmetric crystal/compound assemblies and standard shapes.
Verify:
- flutter test test/engine/math/compound_mass_calculator_test.dart passes cleanly.
""",
    },
    {
        "id": 12,
        "title": "feat: Continuous Field Sensor and Gradient Follower System",
        "role": "AI & Pathfinding Engineer",
        "skill": "skills/ai_pathfinding_engineer.json",
        "target_files": [
            "lib/engine/components/field_sensor.dart",
            "lib/engine/systems/field_sensor_system.dart",
        ],
        "test_files": ["test/engine/systems/field_sensor_system_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: AI & Pathfinding Engineer (see skills/ai_pathfinding_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target files and test file.

Task: Implement FieldSensor component and FieldSensorSystem.
1. Create lib/engine/components/field_sensor.dart:
   - Extension type FieldSensor over Float32List:
     - targetChannel (float cast to int)
     - sensitivity (double, positive = seek peak/heat, negative = flee/avoid)
     - sensorRadius (double)
     - lastSampledValue (double)
     - lastGradientX (double)
     - lastGradientY (double)
2. Create lib/engine/systems/field_sensor_system.dart:
   - Samples scalar grid values at entity Position.
   - Evaluates central difference gradient.
   - Applies proportional steering force to entity Velocity or PreferredVelocity.
   - Zero per-frame allocations.
3. Create test/engine/systems/field_sensor_system_test.dart:
   - 100% test coverage verifying gradient climbing towards high-heat/scent cells and avoidance of toxic/cold cells.
Verify:
- flutter test test/engine/systems/field_sensor_system_test.dart passes cleanly.
""",
    },
    {
        "id": 13,
        "title": "feat: Continuous Field Footprint Deposition System",
        "role": "Simulation Engineer",
        "skill": "skills/simulation_engineer.json",
        "target_files": [
            "lib/engine/components/field_emitter.dart",
            "lib/engine/systems/field_emission_system.dart",
        ],
        "test_files": ["test/engine/systems/field_emission_system_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Simulation Engineer (see skills/simulation_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target files and test file.

Task: Implement FieldEmitter component and FieldEmissionSystem.
1. Create lib/engine/components/field_emitter.dart:
   - Extension type FieldEmitter over Float32List:
     - targetChannel (float as int)
     - emissionRate (amount per second)
     - radius (continuous splat radius)
     - falloffType (0: Bilinear, 1: Gaussian, 2: Flat)
     - isActive (1.0 or 0.0)
2. Create lib/engine/systems/field_emission_system.dart:
   - Queries entities with Position and FieldEmitter.
   - Splats emission value * dt into continuous grid buffers (e.g. heat emission or footstep road pressure).
   - Zero per-frame allocations.
3. Create test/engine/systems/field_emission_system_test.dart:
   - 100% test coverage verifying grid accumulation across multiple moving entities with differing rates and radii.
Verify:
- flutter test test/engine/systems/field_emission_system_test.dart passes cleanly.
""",
    },
    {
        "id": 14,
        "title": "feat: Grid Flow-Field Steering Behavior System",
        "role": "AI & Pathfinding Engineer",
        "skill": "skills/ai_pathfinding_engineer.json",
        "target_files": [
            "lib/engine/components/flow_field_follower.dart",
            "lib/engine/systems/flow_field_steering_system.dart",
        ],
        "test_files": ["test/engine/systems/flow_field_steering_system_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: AI & Pathfinding Engineer (see skills/ai_pathfinding_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target files and test file.

Task: Implement FlowFieldFollower component and FlowFieldSteeringSystem.
1. Create lib/engine/components/flow_field_follower.dart:
   - Extension type FlowFieldFollower over Float32List:
     - alignmentWeight (double, 0.0 to 1.0)
     - maxSpeed (double)
     - lookaheadDistance (double)
2. Create lib/engine/systems/flow_field_steering_system.dart:
   - Samples 2D vector field at entity lookahead position.
   - Adjusts entity Velocity smoothly towards flow direction without allocations.
3. Create test/engine/systems/flow_field_steering_system_test.dart:
   - 100% test coverage verifying streamline following, speed clamping, and smooth turning along vector curves.
Verify:
- flutter test test/engine/systems/flow_field_steering_system_test.dart passes cleanly.
""",
    },
    {
        "id": 15,
        "title": "feat: Spatial Resonance and Distance-Weighted Falloff Math",
        "role": "Mathematics Engineer",
        "skill": "skills/mathematics_engineer.json",
        "target_files": ["lib/engine/math/spatial_resonance.dart"],
        "test_files": ["test/engine/math/spatial_resonance_test.dart"],
        "prompt": """You are an AI Contributor for the Sting game engine (bare-metal 2D ECS in Dart).
Role: Mathematics Engineer (see skills/mathematics_engineer.json).

CRITICAL BOUNDARY: Zero Allocations per frame. Pure dart:ui.
MERGE SAFETY: Do NOT modify lib/sting.dart, pubspec.yaml, or any shared file. ONLY create your target file and test file.

Task: Implement Spatial Resonance and Distance-Weighted Falloff mathematical library.
1. Create lib/engine/math/spatial_resonance.dart:
   - Class SpatialResonance providing pure static functions:
     - gaussianFalloff(double distanceSq, double radiusSq, double peakValue)
     - inverseSquareFalloff(double distanceSq, double softeningFactor, double intensity)
     - smoothstepFalloff(double distance, double innerRadius, double outerRadius)
     - quinticHermiteFalloff(double normalizedDistance)
     - evaluateArrayFalloff(Float32List outBuffer, Float32List distSqBuffer, int count, double radiusSq, double peakValue):
       Batch-processes distance buffers into output buffers with zero allocations.
2. Create test/engine/math/spatial_resonance_test.dart:
   - 100% test coverage verifying boundary conditions, curve monotonicity, and zero division guards.
Verify:
- flutter test test/engine/math/spatial_resonance_test.dart passes cleanly.
""",
    },
]


def dispatch_session(task: dict, auto_pr: bool = True) -> dict:
    url = f"{API_BASE}/sessions"
    headers = {
        "x-goog-api-key": get_api_key(),
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": task["prompt"],
        "title": task["title"],
        "sourceContext": {
            "source": DEFAULT_SOURCE,
            "githubRepoContext": {
                "startingBranch": DEFAULT_BRANCH,
            },
        },
        "automationMode": "AUTO_CREATE_PR" if auto_pr else "AUTOMATION_MODE_UNSPECIFIED",
        "requirePlanApproval": False,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        sys.stderr.write(f"HTTP Error {e.code} for Task {task['id']}: {err}\n")
        return {"error": err, "code": e.code}
    except Exception as e:
        sys.stderr.write(f"Error for Task {task['id']}: {e}\n")
        return {"error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch 15 disjoint tasks to Jules")
    parser.add_argument("--dry-run", action="store_true", help="Print task info without dispatching")
    parser.add_argument("--task", type=int, help="Dispatch only a specific task ID (1-15)")
    parser.add_argument("--registry-file", default="tools/active_sessions.json", help="Path to write active sessions")
    parser.add_argument("--start-task", type=int, default=1, help="Start from a specific task ID")
    args = parser.parse_args()

    # Load existing registry if present
    existing_results = {}
    if os.path.exists(args.registry_file):
        try:
            with open(args.registry_file, "r") as f:
                for entry in json.load(f):
                    existing_results[entry["taskId"]] = entry
        except Exception:
            pass

    selected_tasks = [
        t for t in TASKS
        if (args.task is None or t["id"] == args.task) and t["id"] >= args.start_task
    ]
    print(f"Preparing to dispatch {len(selected_tasks)} tasks to Google Jules...")

    # Verification: Verify 100% disjoint file sets
    all_targets = set()
    all_tests = set()
    for t in TASKS:
        for f in t["target_files"]:
            assert f not in all_targets, f"Collision detected for {f} in task {t['id']}"
            all_targets.add(f)
        for f in t["test_files"]:
            assert f not in all_tests, f"Collision detected for {f} in task {t['id']}"
            all_tests.add(f)
    print("Verified zero file intersection across all 15 tasks!")

    if args.dry_run:
        for t in selected_tasks:
            print(f"\n[DRY RUN] Task {t['id']}: {t['title']}")
            print(f"  Role: {t['role']} ({t['skill']})")
            print(f"  Target Files: {t['target_files']}")
            print(f"  Test Files: {t['test_files']}")
        return

    for t in selected_tasks:
        print(f"\nDispatching Task {t['id']}: {t['title']}...")
        resp = dispatch_session(t)
        s_id = resp.get("id") or resp.get("name", "").split("/")[-1]
        url = resp.get("url", "")
        state = resp.get("state", "UNKNOWN")
        print(f" -> Session ID: {s_id}")
        print(f" -> URL: {url}")
        print(f" -> State: {state}")
        existing_results[t["id"]] = {
            "taskId": t["id"],
            "title": t["title"],
            "role": t["role"],
            "sessionId": s_id,
            "url": url,
            "state": state,
            "targetFiles": t["target_files"],
            "testFiles": t["test_files"],
        }
        # Update registry after each dispatch
        with open(args.registry_file, "w") as f:
            json.dump(list(existing_results.values()), f, indent=2)
        time.sleep(1)  # Stagger requests slightly

    print(f"\nAll sessions dispatched and registered in {args.registry_file}!")


if __name__ == "__main__":
    main()
