# Asset sources

The displayed header uses a content-versioned filename so browsers and image proxies fetch new artwork when it changes. `assets/header-fabio.svg` remains the build source; run `python3 scripts/version_header.py` after updating it to create the versioned copy and update the README image reference. Existing versions are retained for older links.

The SVG assets use a four-color source palette: #101216, #F2F0E8, #7B8494 and #4778FF. The limited palette applies to the graphic assets; project screenshots retain their original colors.

The graphics use contemporary typography, a pixel-art controller / terminal / security introduction with bounded pixel-sweep morph transitions, a pixel adaptation of the Kali dragon spinning 360 degrees in the image plane like a fan propeller, event-to-evidence validation, and reversible state timelines. Game development skills include Unity and Unreal Engine 5, as confirmed by the profile owner. Reduced-motion preferences are supported. The animated structures are conceptual illustrations, not live project measurements.

The Kali dragon is adapted from the [official Kali Linux press pack](https://gitlab.com/kalilinux/documentation/press-pack/-/tree/main/Kali/Logomark), using the standalone `kali-dragon-white.svg` logomark. KALI LINUX™ is a trademark of OffSec. The remaining graphic compositions, apart from the credited technology logos, are original.

Display text uses [Space Grotesk](https://github.com/google/fonts/tree/main/ofl/spacegrotesk), converted to SVG outlines. The license is included in [OFL-SpaceGrotesk.txt](OFL-SpaceGrotesk.txt).

The SVG files require no external fonts, scripts, images or services.

Static pixel-art technology icons are adapted from [Simple Icons](https://github.com/simple-icons/simple-icons) (CC0-1.0) and [Devicon](https://github.com/devicons/devicon) (MIT), rebuilt on a 16×16 pixel grid with the profile palette. Python and Java receive simplified pixel drawings to preserve their recognizable details at small sizes. Exact source URLs and original hashes are in `icons/sources.json`; licenses are included in `icons/`. The BlackArch icon is a pixel redraw of the [official Arch-and-katana logo](https://blackarch.org/images/logo/ba-logo.png). Neutral original utility glyphs represent Nmap (scanner), Hydra (key), John the Ripper (password), JPA (database), Swing (desktop window) and the OpenAI API (AI chip); these glyphs are not official brand marks.

Project insignias in `projects/` are generated separately by `scripts/build_projects.py` from `projects.json`. Their pixel drawings are original and follow the same palette. The clickable gallery concept was inspired by [Gustavo Martins’s profile](https://github.com/gustavomartins-dev). No crest artwork was copied. See `PROJECTS.md` for maintenance instructions and source references.

Nikto and Gobuster use simplified 16×16 pixel redraws of the [Nikto alien](https://www.kali.org/tools/nikto/images/nikto-logo.svg) and [Gobuster speeding globe](https://www.kali.org/tools/gobuster/images/gobuster-logo.svg) published by Kali Linux, using the same profile palette. Reference SVGs and their hashes are retained in `icons/` and `icons/sources.json`; `scripts/build_pixel_icons.py` contains the pixel drawings. Both desktop and mobile toolbox layouts include these tools.
