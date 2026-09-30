import unittest

from preset_test_support import (
    BOOTSTRAP_PATH,
    EXTENSION_ROOT,
    INSTALLER_PATH,
    INSTALL_HOST_PATH,
    INSTALL_SOURCE_PATH,
    PRESET_ROOT,
    SPECKIT_VERSION,
    WORKFLOW_OVERLAY_PATH,
)


class PresetSourceTests(unittest.TestCase):
    def test_manifests_preserve_pinned_spec_kit_composition(self):
        extension = (EXTENSION_ROOT / "extension.yml").read_text(encoding="utf-8")
        preset = (PRESET_ROOT / "preset.yml").read_text(encoding="utf-8")

        self.assertIn(
            f'speckit_version: "=={SPECKIT_VERSION}"',
            extension,
        )
        self.assertIn(
            f'speckit_version: "=={SPECKIT_VERSION}"',
            preset,
        )
        self.assertIn('version: "==0.1.0"', preset)
        self.assertEqual(1, preset.count('strategy: "append"'))
        self.assertIn('name: "speckit.tasks"', preset)
        self.assertNotIn('name: "speckit.plan"', preset)
        self.assertNotIn('name: "speckit.converge"', preset)

    def test_adapter_uses_boundary_public_identities(self):
        extension = (EXTENSION_ROOT / "extension.yml").read_text(encoding="utf-8")
        preset = (PRESET_ROOT / "preset.yml").read_text(encoding="utf-8")
        overlay = WORKFLOW_OVERLAY_PATH.read_text(encoding="utf-8")
        installer = INSTALLER_PATH.read_text(encoding="utf-8")
        bootstrap = BOOTSTRAP_PATH.read_text(encoding="utf-8")

        self.assertIn("id: boundary", extension)
        self.assertIn('name: "Boundary Spec Kit Adapter"', extension)
        self.assertIn('id: "boundary"', preset)
        self.assertIn("- id: boundary", preset)
        self.assertIn('id: "boundary"', overlay)

        for declaration in (
            'readonly EXTENSION_ID="boundary"',
            'readonly PRESET_ID="boundary"',
            'readonly WORKFLOW_OVERLAY_ID="boundary"',
        ):
            self.assertIn(declaration, installer)

        for declaration in (
            'readonly BOUNDARY_EXTENSION_ID="boundary"',
            'readonly BOUNDARY_PRESET_ID="boundary"',
            'readonly WORKFLOW_OVERLAY_ID="boundary"',
        ):
            self.assertIn(declaration, bootstrap)

    def test_extension_exposes_only_boundary_adapter_transitions(self):
        manifest = (EXTENSION_ROOT / "extension.yml").read_text(encoding="utf-8")

        for command in (
            "speckit.boundary.authorize",
            "speckit.boundary.verify",
        ):
            self.assertIn(command, manifest)

        self.assertNotIn("hooks:", manifest)
        for hook in (
            "after_plan:",
            "after_tasks:",
            "before_implement:",
            "after_implement:",
        ):
            self.assertNotIn(hook, manifest)

    def test_bootstrap_uses_codex_and_local_boundary_source(self):
        content = BOOTSTRAP_PATH.read_text(encoding="utf-8")

        for marker in (
            'readonly ACTIVE_INTEGRATION="codex"',
            'readonly ACTIVE_COMMANDS_DIR=".agents/skills"',
            'readonly SPECKIT_SCRIPT_OVERRIDE="${BOUNDARY_SPECKIT_SCRIPT:-}"',
            'args+=(--script "$SPECKIT_SCRIPT_OVERRIDE")',
            "bash scripts/install.sh --source .",
        ):
            self.assertIn(marker, content)

        self.assertNotIn("--integration generic", content)
        self.assertNotIn("--script ps", content)

    def test_installer_materializes_native_runtime(self):
        installer = INSTALLER_PATH.read_text(encoding="utf-8")
        source_helper = INSTALL_SOURCE_PATH.read_text(encoding="utf-8")
        host_helper = INSTALL_HOST_PATH.read_text(encoding="utf-8")
        content = "\n".join((installer, source_helper, host_helper))

        for marker in (
            f'readonly SPECKIT_VERSION="{SPECKIT_VERSION}"',
            'readonly ACTIVE_INTEGRATION="codex"',
            'readonly CODEX_SKILL_ADAPTER="adapters/codex/materialize.py"',
            'readonly BOUNDARY_RUNTIME_DIR=".specify/boundary-runtime"',
            'readonly SPECKIT_SCRIPT_OVERRIDE="${BOUNDARY_SPECKIT_SCRIPT:-}"',
            'source "$INSTALL_SCRIPT_DIR/install-source.sh"',
            'source "$INSTALL_SCRIPT_DIR/install-host.sh"',
            "specify extension add",
            "specify preset add",
            "specify workflow overlay add",
            "specify workflow overlay remove",
            'local args=(integration switch "$ACTIVE_INTEGRATION")',
            'args+=(--script "$SPECKIT_SCRIPT_OVERRIDE")',
            "materialize_boundary_runtime",
            "materialize_boundary_skills",
            "src/boundary/__init__.py",
        ):
            self.assertIn(marker, content)

        for forbidden in (
            "npm install",
            "pip install",
            "specify bundle install",
        ):
            self.assertNotIn(forbidden, content)

    def test_shell_sources_remain_small(self):
        for path in (
            BOOTSTRAP_PATH,
            INSTALLER_PATH,
            INSTALL_SOURCE_PATH,
            INSTALL_HOST_PATH,
        ):
            with self.subTest(path=path.name):
                self.assertLessEqual(
                    len(path.read_text(encoding="utf-8").splitlines()),
                    250,
                )

    def test_task_augmentation_uses_on_demand_inspection_and_exact_writes(self):
        tasks = (PRESET_ROOT / "commands" / "tasks.md").read_text(encoding="utf-8")

        for marker in (
            "## Boundary Write Scope",
            "boundary inspect <target...>",
            "Writes:",
            "durable project record",
            "declared-scope preflight",
            "grants no implementation authority",
            "speckit.boundary.authorize",
            "Do not create or refresh a persisted Boundary context projection",
            "Do not add a separate validation lifecycle phase",
        ):
            self.assertIn(marker, tasks)


if __name__ == "__main__":
    unittest.main()
