# 3D Eye Model — Sourcing & Adaptation

## Current model status

| Item | Status |
| --- | --- |
| Built-in model | Procedural WebGL anatomy (no external file) |
| GLB drop-in path | `public/models/anatomical-eye.glb` |
| License of built-in model | This repository’s own code (three.js primitives) |

## What is shipped today

The Eye Anatomy Explorer on the Screening Result page renders a **real-time procedural 3D
anatomical eye** built from separate Three.js meshes (not a CSS/SVG/image fake):

- Sclera (translucent in Internal view)
- Cornea (clearcoat, ior 1.376)
- Iris (procedural iris texture, radial striations)
- Pupil
- Lens (biconvex, translucent)
- Vitreous body
- Retina (posterior cup )
- Choroid (vascular layer between sclera and retina)
- Macula
- Optic disc
- Optic nerve (tubular extension toward the posterior orbit)
- Retinal blood vessels (decorative anatomy — **not** the patient’s vessels)

This model is genuine WebGL geometry that users can rotate, zoom, pan, x-ray, explode and
isolate. It is **not** presented as the patient’s retina.

## Why a GLB is not bundled yet

Per the project’s licensing rule, we do not silently bundle a downloaded copyrighted model.
A searchable, clearly-licensed superior anatomical eye GLB (CC0 / CC-BY / medical-domain) is
the preferred replacement. When one is selected:

1. Place it at `public/models/anatomical-eye.glb`.
2. Add the license + attribution to this file.
3. In `src/components/eye/EyeModel.tsx`, load it once via `useGLTF` and map the actual scene
   graph node names to the structure ids in `src/data/eyeAnatomy.ts` using an `eyeStructureMap`
   (e.g. `{ sclera: 'Sclera_node', iris: 'Iris_node', ... }`).
4. Keep the structure ids and camera/preset logic unchanged — the viewer is data-driven.

## Model file layout (future)

```
public/models/anatomical-eye.glb
```

## Anatomy data mapping

Structure configuration lives in `src/data/eyeAnatomy.ts` (`EYE_STRUCTURES`). Each entry holds:

- label + educational description/detail
- 3D anchor (`base`) and explode direction (`explode`)
- label screen-anchor (`labelAnchor`)
- camera focus distance
- visibility / transparency behaviour (internal view)

`useEyeModel` (`src/hooks/useEyeModel.ts`) exposes `structures` and `structureMap`; it is the
single place where GLB node-name mapping should be inserted for a future file-based model.

## Attribution requirements (for the future file)

When a file model is added, record here:

- Model source / URL
- Author / provider
- License (and whether commercial/web use is allowed)
- Attribution text to include
- Modifications made (remeshing, Draco compression, texture resizing)
- Optimization steps (polygon count, texture sizes, material count)