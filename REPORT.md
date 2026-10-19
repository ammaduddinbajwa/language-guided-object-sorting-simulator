# Assignment report

## Objective
Demonstrate a small language-guided manipulation pipeline using images, classical vision, symbolic checks and search. A user describes a coloured object and tray. The system detects the object, estimates a grasp centre and width, finds a route, executes a simulated transfer, and checks the resulting image.

## Method
Scenes are 640 × 400 pixels with three coloured rigid shapes, known trays and dark obstacles. HSV segmentation separates colours. Contours provide centroids, dimensions and polygon-based shape estimates. The planner receives only the image and command. The simulator's object metadata is used by rendering, execution and evaluation, never by perception/planning.

Commands follow a restricted grammar. Ambiguous descriptions are rejected. The opening limit is 50 pixels. Obstacles and other objects are dilated by half the selected bounding-box diagonal plus three pixels. Free-space connectivity rejects unreachable destinations; four-connected A* finds a unit-cost carrying route. Destination centres must keep the payload inside the tray. Verification detects objects again and requires both departure from the source and a new matching detection inside the destination.

## Measured results
Nine automated functional tests passed. Evaluation used 100 trials across held-out scene seeds 100–119 (20 per case).

| Case | Expected result | Correct / trials |
|---|---|---|
| Normal | Verified placement | 20 / 20 |
| Oversized | Rejected | 20 / 20 |
| Ambiguous | Rejected | 20 / 20 |
| Blocked destination | Rejected | 20 / 20 |
| Injected grasp failure | Verification fails | 20 / 20 |

Perception matched object counts, colours, shapes and centres in all 100 scenes. Selection was correct in all 40 accepted plans, including intentionally failed executions. Mean perception/selection/planning time for accepted plans was 13.136 ms on this run; hardware and load affect timing. These are measured synthetic results, not estimates of real robot performance. Raw rows and dependency versions are supplied in evidence/.

## Evidence
The PNG files are actual algorithm outputs. 01 shows the input camera image, 02 overlays detections and the planned route, 03 shows verified placement, and 04 shows a carrying route crossing the scene around obstacles. They are not browser screenshots or real camera photographs.

## Interpretation
The project demonstrates Python, image-based perception, constrained language understanding, geometry-based manipulation checks, collision-aware planning, evaluation and safety rejection. It does not use machine learning or train on examples. Holding out seeds tests combinations and layouts within a known synthetic generator, not novel semantic categories.

## Limitations
No physical dynamics, joints, grip force, depth, rotation or contact simulation. Approach is assumed overhead; only payload transfer is collision-planned. Colour thresholds and trays are calibrated. Verification shares the detector and can therefore share its errors. All success rates apply only to these clean synthetic tests. Further work should include noisy/occluded scenes, richer shapes, physically simulated grasps and a separately tested verifier.
