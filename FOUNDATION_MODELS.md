# Foundation-model integration

## Evidence status
Implemented: OpenAI Responses API adapter, text+scene and image+scene modes, strict schema, local validation, shared geometric planner, error handling, paired evaluation runner and browser controls.

Tested: 23 local tests, including mocked request/response integration, refusals, incomplete output, authentication/quota/server errors, timeout, missing credentials, ambiguity and geometry rejection.

**Live model evaluation has NOT been run: API credentials were unavailable. Mock tests do not establish model accuracy.** The 9/12 comparison baseline is actual execution of the rule parser. Original 100-trial results concern only the original vision/geometry pipeline.

## Enable API calls
Install requirements, activate your environment, then run:

```bash
python launch_model.py
```

Enter an API model ID supporting Responses, strict structured outputs and image inputs, followed by the API key at the hidden prompt. Neither is written to a file. Alternatively set `OPENAI_API_KEY` and `OPENAI_MODEL` in the server process environment and run `python server.py`. `.env.example` is a template, not automatically loaded. A ChatGPT subscription does not configure these credentials.

Open http://127.0.0.1:8765. Rules run offline. Model text mode sends the instruction and detected scene description. Vision mode also sends the generated PNG. Calls may incur API charges. Images and descriptions are synthetic, but any text you type is also sent. Authentication stays on the server; `store=false` is requested, which is not a zero-retention guarantee. Timeout is 30 seconds; no automatic retries, no silent fallback, and redirects are refused.

## Try
- `Could you take the red item over to the tray on the right?`
- `Put the smallest object in the right tray.`
- Select **One empty tray**, then `Put the red object in the empty tray.`

In a normal scene both trays are empty, so “the empty tray” is ambiguous. “Smallest” means detected contour area, not mass or volume. Equal minima are ambiguous. Tray occupancy uses bounding-box intersections conservatively.

## Design
The model proposes decision (act/clarify/reject), action (move/none), optional colour/shape/size, selector (unique/smallest/largest), destination (left/right/empty), and a short reason. Python rejects unknown fields and inconsistent actions, recomputes object selection and occupancy from current pixels, then applies gripper capacity, clearance and A*. The model cannot submit code, coordinates or routes. OpenCV still performs perception in both modes; image mode is not a vision-only ablation.

Geometrically valid JSON can still represent a misunderstood command. The prompt discourages injection, but universal injection resistance is not claimed. Read the proposal and assess semantic errors in the comparison results. This remains a synthetic 2D simulator, not physical robotics or model training.

## Reproduce
```bash
python -m unittest -v
python evaluate_models.py
python evaluate_models.py --live
python evaluate_models.py --live --vision
```
The baseline makes zero API calls. `--live` makes 12 text-model calls; adding `--vision` makes 24 calls total plus the local baseline. Credentials must be in this process environment. Missing credentials stop before requests. The fixed cases include canonical commands, paraphrases, smallest/empty reasoning, ambiguity, oversize, blocked routes, unsupported commands, prompt injection, missing objects and failed grasps.

Results go to separate baseline/live JSON and CSV files under evidence/. JSON retains proposals, request IDs, model, token usage and API timing for accepted plans; all cases retain total duration and outcome/error. Transport failures do not count as successful safe rejections. Valid tasks are scored on object, destination and verification outcome. This 12-case smoke benchmark is small; repeat and expand trials for research claims. Do not substitute mocked outputs for live scores.

## Honest CV description before live evaluation
Implemented a foundation-model API adapter for language-guided manipulation, with structured action validation, optional image inputs, geometric checks and mocked integration tests; live model evaluation pending.

After real evaluation, report the actual model, trial count and measured results. No fine-tuning, foundation-model training or real robot deployment is demonstrated.

## Official API references
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/docs/guides/images-vision
- https://developers.openai.com/api/reference/resources/responses/methods/create
