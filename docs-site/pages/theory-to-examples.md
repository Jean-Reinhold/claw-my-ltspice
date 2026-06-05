# Theory To Examples

The example catalog is informed by the EB2 theoretical material under the local
course folder `/Users/jeanreinhold/Documents/comp/eb2/documentos/material_teorico`.
The documentation and circuits here are original implementations and summaries;
the project does not copy PDF text, figures, or proprietary model files.

## Source Themes Reviewed

The material covers a broad analog electronics sequence:

- amplifier interfaces, gain, impedance, and controlled-source abstractions
- transistor amplifier stages and differential pairs
- ideal and nonideal operational amplifiers
- inverting, non-inverting, summing, difference, and instrumentation amplifiers
- integrators, differentiators, active filters, and Sallen-Key responses
- logarithmic, antilogarithmic, square-root, limiter, clipper, and conformer circuits
- comparators, references, window comparators, and Schmitt triggers
- sample-and-hold circuits, quantization, flash ADCs, SAR ADCs, DACs, and R-2R ladders
- waveform generators, relaxation oscillators, 555 timers, Wien bridge, twin-T, and phase-shift oscillators

## Implemented First-Batch Examples

The first batch favors examples that are useful, visually readable, and likely to
remain stable in Docker/LTspice CI.

| Example | Theory Source Theme | Why It Was Added |
| --- | --- | --- |
| `precision-rectifier` | nonlinear op-amp/diode shaping | shows active diode-drop compensation with repo-owned models |
| `sallen-key-lowpass` | active filters and Sallen-Key topology | adds a second-order filter with time-domain and FFT evidence |
| `diode-clipper-spectrum` | diode limiters and conformer/waveshaping circuits | demonstrates clipping and harmonic generation with FFT |
| `rlc-step-ringing` | second-order transient response | introduces damping, overshoot, and ringing measurements |
| `passive-rc-spectrum-split` | first-order filter frequency selectivity | shows low-pass/high-pass separation and spectrum inspection |
| `opamp-practical-integrator` | op-amp integrators | documents bounded practical integration using feedback leakage |
| `opamp-practical-differentiator` | op-amp differentiators | documents bounded edge/frequency response using practical limiting |
| `sallen-key-highpass` | active high-pass filters | complements the low-pass example with high-frequency selection |

## Deferred Candidates

These are good later examples, but they carry more layout, modeling, or CI risk:

- instrumentation amplifier with Wheatstone bridge stimulus and CMRR measurements
- Schmitt trigger with hysteresis threshold extraction
- window comparator with reference ladder
- R-2R DAC and small flash ADC transfer examples
- relaxation oscillator with square and ramp outputs
- log/antilog amplifier using diode or transistor exponential behavior
- BJT differential pair with common-mode and differential gain checks

## Model Policy Applied

The examples intentionally avoid copying textbook/vendor SPICE models. The first
batch uses:

- passive R, L, and C elements
- the repo-owned `CLAW_IDEAL_OPAMP` educational macromodel
- the inline repo-owned `DCLAW` educational diode model
- bundled `.asy` symbols for rendered examples

Any future vendor model must be reviewed and recorded in `models/manifest.toml`
before it is committed.

## Documentation Pattern

Each implemented example should provide:

- a Python generator that emits `.cir` and `.asc`
- explicit schematic `WIRE`, `FLAG`, and `IOPIN` records
- `.meas` values that can be checked from the LTspice `.log`
- an expected time-domain plot
- FFT plots when spectral content is part of the lesson
- schematic rendering through the real `ltspice_to_svg` toolchain
