# Layout spec — Wave Planning slide (house design)

The generator implements all of this; read it only if you need to adjust the script.

## Canvas
MobiLab template, 45.2 × 25.4 cm (17.795" × 10"), white background, 0.6" side margins.

## Header
- Title: Aeonik Semibold ~34 pt, `#192832`.
- Subtitle: Aeonik Medium ~18 pt, `#3D627B`.

## Columns (1–3)
- 0.4" gutter. Week header band: rounded rectangle, MobiLab teal `#00A89D`;
  left label Aeonik Medium ~20 pt white bold, right meta Inter ~12 pt white.

## Unit cards
Rounded rectangle `#F2F2F2` with:
- Left status marker (0.07"): white + `#B0B0B0` outline = Scheduled; amber `#FBBB33` = Planned.
- Date chip `DD Mon`, Inter SemiBold ~12 pt.
- Line 1: unit identifier, Inter SemiBold ~12.5 pt (+ optional amber note marker).
- Line 2: `workload  ·  owner`, Inter ~10.5 pt `#6B6B6B`.
- Optional scenario chip at the right: pill `#E0F4F2`, Inter SemiBold 9 pt `#00756D`.
- Three-column layouts drop to 11.5 / 9.5 pt.

### Dimmed (missing) cards
Fill `#E8E8E8`, text `#A6A6A6`, workload/owner shown as `—`.

### Adaptive sizing
Card height 0.42"–0.62", gap 0.08"–0.12", driven by the tallest column and the number
of footnotes so everything clears the legend and footer.

## Footnotes, legend, footer
- Footnotes: Inter 10 pt grey, stacked above the legend.
- Legend: outlined dot `Scheduled`, amber dot `Planned`, chip swatch
  `R-factor / scenario` (only when chips are used).
- Footer: `[MOBILAB] | [client logo or name] | Confidential`, page number bottom-right.
  The client logo height (0.25") is the reference; the MobiLab wordmark is ~0.55× that.
  Logos are real PNGs sized by their true aspect ratio.
