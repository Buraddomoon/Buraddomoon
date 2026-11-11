# Maintaining the project gallery

Each insignia represents a repository. All projects have equal visual weight, with no ranks, scores or award positions. The order in `projects.json` controls only the reading order of the gallery.

To add or reorder a project, edit that file and run:

```sh
python3 scripts/build_projects.py
```

The generator rebuilds the individual animated SVGs and the README section between `PROJECTS:START` and `PROJECTS:END`. It uses Python's standard library, requires no API credentials, and leaves the rest of the README untouched. Projects are grouped in rows of three, with proportional image widths that fit the GitHub profile column. The “Explore all repositories” link also leads to projects that do not yet have an insignia.

Use verified descriptions and source links. Keep `summary` brief enough for one line and `stack` to a few technologies. Available emblem drawings are `defense-test`, `reticle`, `cyberlab`, `helmet`, `correlation`, `shield`, `rewind`, `review`, `checkpoint`, `forms`, `platformer`, and `tasks`; a new drawing can be added to `frame()` in the generator. Each emblem has its own animation and a static fallback for reduced-motion preferences.

The current selection uses public repository code and documentation. DevReview AI is identified as a hackathon prototype because the structural and source-code analysis functions are placeholders. FirebaseForms is included at the profile owner’s request, with Swing forms and Firebase Realtime Database operations. Tarefas API adds a focused backend example with explicit controller, service, DTO, mapper and repository layers. Other book CRUD projects and the older portfolio were left out to keep the selection focused; forks are not presented as original projects.

Visual inspiration: the idea of clickable project crests in [Gustavo Martins's profile](https://github.com/gustavomartins-dev). The pixel drawings here are original and use this profile's existing palette.

Technology labels include static 16×16 pixel icons embedded by `scripts/technology_icons.py`. When adding a new technology, add its source SVG under `assets/icons/`, add its name to `ALIASES`, and regenerate its pixel version with `scripts/build_pixel_icons.py` (requires `fonttools`). Record third-party sources and licenses alongside the existing icons. The generated assets are embedded at build time, so the profile does not load icons from an external service.
