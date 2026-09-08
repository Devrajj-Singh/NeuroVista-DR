export type EyeStructureId =
  | 'sclera'
  | 'cornea'
  | 'iris'
  | 'pupil'
  | 'lens'
  | 'vitreous'
  | 'retina'
  | 'choroid'
  | 'macula'
  | 'opticDisc'
  | 'opticNerve'
  | 'vessels';

export type EyeStructure = {
  id: EyeStructureId;
  label: string;
  description: string;
  detail: string;
  color: string;
  base: [number, number, number];
  explode: [number, number, number];
  labelAnchor: [number, number, number];
  focusDistance: number;
  outer?: boolean;
  internalOpacity: number;
};

export const EYE_STRUCTURES: EyeStructure[] = [
  {
    id: 'sclera',
    label: 'Sclera',
    description:
      'The tough white outer layer that gives the eyeball its shape and protects the internal structures.',
    detail:
      'Composed of dense collagenous connective tissue; it anchors the extraocular muscles and ranges 0.3–1.0 mm in thickness.',
    color: '#38ddf8',
    base: [0, 0, 0],
    explode: [0, 0, 0.03],
    labelAnchor: [0.9, 0.7, 0.15],
    focusDistance: 3.6,
    outer: true,
    internalOpacity: 0.16,
  },
  {
    id: 'cornea',
    label: 'Cornea',
    description:
      'The clear, dome-shaped front window of the eye that focuses most incoming light.',
    detail:
      'Avascular and highly innervated; provides about two-thirds of the eye\u2019s refractive power (approx. 43 dioptres).',
    color: '#38ddf8',
    base: [0, 0, 0.96],
    explode: [0, 0, 0.14],
    labelAnchor: [0.62, 0.6, 1.05],
    focusDistance: 2.3,
    internalOpacity: 0.3,
  },
  {
    id: 'iris',
    label: 'Iris',
    description:
      'The coloured ring behind the cornea that controls how much light enters the eye.',
    detail:
      'A contractile diaphragm whose radial and circular muscles change pupil diameter from approx. 2 mm to 8 mm.',
    color: '#14b8a6',
    base: [0, 0, 0.66],
    explode: [0, 0, 0.12],
    labelAnchor: [-0.42, 0.55, 0.78],
    focusDistance: 1.8,
    internalOpacity: 1,
  },
  {
    id: 'pupil',
    label: 'Pupil',
    description: 'The dark central opening of the iris through which light passes.',
    detail:
      'Not a structure itself but an aperture; it constricts in bright light and dilates in dim light.',
    color: '#14b8a6',
    base: [0, 0, 0.7],
    explode: [0, 0, 0.12],
    labelAnchor: [0.12, -0.35, 0.98],
    focusDistance: 1.7,
    internalOpacity: 1,
  },
  {
    id: 'lens',
    label: 'Lens',
    description:
      'A flexible, transparent disc behind the iris that fine-tunes focus for near and far vision.',
    detail:
      'Biconvex and elastic; changes curvature through accommodation, adding up to approx. 20 dioptres of focusing power.',
    color: '#14b8a6',
    base: [0, 0, 0.36],
    explode: [0, 0, 0.22],
    labelAnchor: [0, -0.45, 0.72],
    focusDistance: 2.0,
    internalOpacity: 0.35,
  },
  {
    id: 'vitreous',
    label: 'Vitreous Body',
    description:
      'The clear jelly-like substance filling the space behind the lens and supporting the retina.',
    detail:
      '99% water with collagen and hyaluronic acid; maintains intraocular pressure and holds the retina in place.',
    color: '#38ddf8',
    base: [0, 0, 0],
    explode: [0, 0, 0.28],
    labelAnchor: [0.15, -0.8, 0.1],
    focusDistance: 3.2,
    internalOpacity: 0.12,
  },
  {
    id: 'retina',
    label: 'Retina',
    description:
      'The light-sensitive tissue lining the inside of the back of the eye. It converts light into nerve signals.',
    detail:
      'Contains photoreceptors (rods and cones) and is ten layers thick. Diabetic retinopathy damages its vessels.',
    color: '#14b8a6',
    base: [0, 0, -0.82],
    explode: [0, 0, -0.16],
    labelAnchor: [0.55, -0.25, -1.04],
    focusDistance: 2.2,
    internalOpacity: 0.95,
  },
  {
    id: 'choroid',
    label: 'Choroid',
    description:
      'The dark, richly vascular layer between the sclera and retina that nourishes the retina.',
    detail:
      'Contains the highest blood flow per gram of tissue in the body; its melanin absorbs stray light.',
    color: '#38ddf8',
    base: [0, 0, -0.88],
    explode: [0, 0, -0.06],
    labelAnchor: [-0.62, -0.25, -0.98],
    focusDistance: 2.7,
    outer: true,
    internalOpacity: 0.4,
  },
  {
    id: 'macula',
    label: 'Macula',
    description:
      'The small central region of the retina responsible for sharp, detailed central vision.',
    detail:
      'Contains the highest concentration of cones; its centre, the fovea, gives the clearest visual acuity.',
    color: '#14b8a6',
    base: [0.18, 0.02, -0.78],
    explode: [0, 0, -0.05],
    labelAnchor: [0.48, 0.12, -1.0],
    focusDistance: 1.6,
    internalOpacity: 1,
  },
  {
    id: 'opticDisc',
    label: 'Optic Disc',
    description:
      'The pale blind spot where the optic nerve and retinal blood vessels enter the eye.',
    detail:
      'Contains no photoreceptors, creating the physiological blind spot; swollen discs can indicate raised pressure.',
    color: '#14b8a6',
    base: [0, 0, -0.84],
    explode: [0, 0, -0.07],
    labelAnchor: [0.42, 0.42, -0.98],
    focusDistance: 1.7,
    internalOpacity: 1,
  },
  {
    id: 'opticNerve',
    label: 'Optic Nerve',
    description:
      'The cable of fibre that carries visual signals from the retina to the brain.',
    detail:
      'About 1.2 million retinal ganglion cell axons; continuous with the brain and surrounded by meninges.',
    color: '#38ddf8',
    base: [0, -0.12, -1.5],
    explode: [0, 0, -0.12],
    labelAnchor: [0.4, -0.55, -1.7],
    focusDistance: 2.4,
    internalOpacity: 1,
  },
  {
    id: 'vessels',
    label: 'Retinal Blood Vessels',
    description:
      'The arteries and veins that supply blood across the inner surface of the retina.',
    detail:
      'Visible on fundus photography; their appearance is central to screening diabetic retinopathy. Shown here as anatomy only.',
    color: '#14b8a6',
    base: [0, 0, -0.84],
    explode: [0, 0, -0.1],
    labelAnchor: [-0.35, 0.45, -1.02],
    focusDistance: 2.2,
    internalOpacity: 1,
  },
];

export type CameraPreset = 'front' | 'back' | 'left' | 'right' | 'top' | 'bottom' | 'reset';

export const CAMERA_PRESETS: { id: CameraPreset; label: string }[] = [
  { id: 'front', label: 'Front' },
  { id: 'back', label: 'Back' },
  { id: 'left', label: 'Left' },
  { id: 'right', label: 'Right' },
  { id: 'top', label: 'Top' },
  { id: 'bottom', label: 'Bottom' },
  { id: 'reset', label: 'Reset' },
];

export function getEyeStructure(id: EyeStructureId | null | undefined): EyeStructure | undefined {
  if (!id) return undefined;
  return EYE_STRUCTURES.find((s) => s.id === id);
}