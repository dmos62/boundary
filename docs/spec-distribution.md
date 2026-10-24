# Distribution and Installation

Boundary is a conventional Python CLI selected and locked by mise from its Git source. The installed `boundary` executable is the command surface; Boundary maintains no separate revision or dependency lock and requires no copied runtime or project launcher.

A downstream repository installs its mise-locked Boundary version, then runs `boundary setup install` and `boundary setup check` to manage the root `.gitignore` block for local evidence. Optional skills use `boundary skills install|check|remove --directory PATH`, with an explicit repository-relative destination. These commands do not install or inspect a planning system or agent runtime. Mutating commands refuse open operations.

An external planning system may invoke the versioned generic request CLI without loading Boundary as a Python dependency. A tool upgrade must not silently adopt old operation evidence. Resolve any open operation with the old version before upgrading, then follow the cleanup steps in [setup-downstream.md](setup-downstream.md).

Development uses the repository mise tasks: `dev-install`, `contracts-check`, `test-distribution`, and `test`. Locked source identity belongs to mise project state. Boundary's Python metadata defines runtime dependency compatibility.
