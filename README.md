# Language-Guided Object Sorting Simulator

An assignment-scale browser application demonstrating rule-based language understanding, object selection, action sequencing, capacity validation, and a 2D animated pick-and-place simulation.

## Run
Open `dist/index.html` in a browser. No installation, API key, robot, or backend required. Alternatively run `python3 -m http.server 8000 --directory dist` and open http://localhost:8000.

## Test
Run `node test.cjs` (Node.js required). Nine checks cover selection, destination parsing, ambiguity, oversize rejection, missing objects, unsupported commands, invalid destinations, conflicting descriptions, and already-sorted objects.

## Try
- Move the small blue block to the left tray.
- Put the green circle into the right tray.
- Move the blue object to the left tray. (Ambiguous.)
- Move the large blue block to the right tray. (Too large.)

The parser accepts move/put/place/sort, red/blue/green, small/large, block/circle (square/disk aliases), and left/right tray or bin. No arbitrary natural language or multi-step commands are supported.

## Architecture
`dist/engine.js`: pure deterministic parser, object selection, and validation.
`dist/app.js`: scene state, SVG rendering, animation, session metrics, CSV export.
`dist/style.css`: responsive interface.
`dist/index.html`: interface and scope documentation.

Pipeline: instruction → constrained grammar → object matching → ambiguity and capacity checks → pick/transfer/release sequence → state verification.

## Assignment evaluation
Reset the scene between independent experiments. Run valid commands plus ambiguous, missing-object, and oversized-object cases. Export the session CSV. Report successful valid tasks separately from correctly rejected invalid tasks. Duration is UI execution time including animation, not robot latency. Reset retains logs; reload starts a fresh session.

## Limitations
This project uses JavaScript for a self-contained browser experience, not Python. It has no trained AI model, computer vision, physical dynamics, inverse kinematics, or obstacle avoidance. Coordinates and properties come from simulator state. A virtual overhead lift is assumed during transfer. The gripper capacity is 50 abstract units; the large block is 70. Objects have predefined properties; this does not demonstrate generalisation to unseen physical objects. External Google Fonts are optional; fallback fonts work offline. All command processing stays in the browser.

## Skills demonstrated
Programming, constrained language parsing, symbolic reasoning, state management, action sequencing, interactive simulation, validation, and experimental reporting.
