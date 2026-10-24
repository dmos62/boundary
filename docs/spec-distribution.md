# Distribution and Installation

Boundary is a conventional Python CLI selected and locked by mise from its Git source. The installed `boundary` executable is the command surface; Boundary maintains no separate revision or dependency lock and requires no copied runtime or project launcher.

A downstream repository installs its mise-locked Boundary version, then runs `boundary integration install` and `boundary integration check` to materialize Boundary agent skills and the managed root `.gitignore` block. Those commands do not install or inspect a planning system. Removing Boundary-owned generated skills uses `boundary integration remove` after open operations are closed.

An external planning system may invoke the versioned generic request CLI without loading Boundary as a Python dependency. A tool upgrade must not silently adopt old operation evidence. Resolve any open operation with the old version before upgrading, then follow the cleanup steps in [setup-downstream.md](setup-downstream.md).

Development uses the repository mise tasks: `dev-install`, `contracts-check`, `test-distribution`, and `test`. Locked source identity belongs to mise project state. Boundary's Python metadata defines runtime dependency compatibility.
