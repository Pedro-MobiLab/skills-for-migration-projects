# Cover slide

`assets/cover-template.pptx` is a one-slide MobiLab deck with the branded dark-teal
cover (MobiLab partner badges included). Its three placeholders hold neutral text:

| Placeholder name | Neutral text | Fill with |
|---|---|---|
| `Main Cover Title` | `Client Programme Name` | the programme, e.g. `Contoso Cloud Migration` (`client.programme`) |
| `Subtitle` | `Wave Planning – CWxx & CWyy` | e.g. `Wave Planning – CW29 & CW30` |
| `Location - Date` | `dd – dd Month yyyy` | e.g. `13 – 25 July 2026` |

You don't need to edit the template: pass a `cover` block in the data JSON together
with `"_template": "assets/cover-template.pptx"` and `"_keep_cover": true`. The
generator writes the text into those placeholders (keeping the formatting) and adds
the wave slide as slide 2.

## Partname hygiene (if you ever rebuild the cover template)
If you strip a larger deck down to one slide, remove orphaned slide parts physically
(unpack → drop extra `<p:sldId>` entries from `presentation.xml` → run the pptx skill's
`clean.py` → repack). Removing entries only from the slide-id list leaves the old parts
in the package and `python-pptx` fails with `Duplicate name: ppt/slides/slideN.xml`.

## Logos
- `assets/logo-mobilab.png` — MobiLab wordmark, always used.
- Client logo — passed per run via `client_logo` (keep client logos in the engagement's
  own space, not in this repo). The generator sizes logos by their real aspect ratio.
