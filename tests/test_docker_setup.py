from __future__ import annotations

import os
import unittest
from pathlib import Path


class DockerSetupTests(unittest.TestCase):
    def test_host_wrapper_is_executable_and_docker_first(self) -> None:
        wrapper = Path("claw-spice")
        text = wrapper.read_text()

        self.assertTrue(os.access(wrapper, os.X_OK))
        self.assertIn("docker compose", text)
        self.assertIn("open_svg", text)
        self.assertIn("/workspace/", text)

    def test_dockerfile_installs_ltspice_and_project(self) -> None:
        dockerfile = Path("Dockerfile").read_text()

        self.assertIn("LTSPICE_MSI_URL", dockerfile)
        self.assertIn("winehq", dockerfile)
        self.assertIn("xvfb", dockerfile.lower())
        self.assertIn("pip install", dockerfile)
        self.assertIn(".[runtime,docs,dev]", dockerfile)
        self.assertIn("find /opt/ltspice -type d -exec chmod a+rwx", dockerfile)
        self.assertIn("find /opt/ltspice -type f -exec chmod a+rw", dockerfile)

    def test_prebuilt_dockerfile_documents_fallback(self) -> None:
        dockerfile = Path("Dockerfile.prebuilt").read_text()

        self.assertIn("aanas0sayed/docker-ltspice:macos-latest", dockerfile)
        self.assertIn(".[runtime,docs,dev]", dockerfile)
        self.assertIn("claw-spice-entrypoint", dockerfile)

    def test_ltspice_wrapper_waits_for_wine_children(self) -> None:
        wrapper = Path("docker/ltspice").read_text()

        self.assertIn("wine \"$LTSPICE_EXE\"", wrapper)
        self.assertIn("wineserver -w", wrapper)
        self.assertNotIn("exec wine", wrapper)

    def test_entrypoint_sets_writable_xdg_paths_for_wine(self) -> None:
        entrypoint = Path("docker/entrypoint.sh").read_text()

        self.assertIn("XDG_RUNTIME_DIR", entrypoint)
        self.assertIn("XDG_CACHE_HOME", entrypoint)
        self.assertIn("XDG_CONFIG_HOME", entrypoint)
        self.assertIn("/tmp/claw-home-$(id -u)", entrypoint)
        self.assertIn("[ ! -w \"$HOME\" ]", entrypoint)
        self.assertIn("chmod 700 \"$XDG_RUNTIME_DIR\"", entrypoint)

    def test_compose_uses_linux_amd64_and_workspace_mount(self) -> None:
        compose = Path("docker-compose.yml").read_text()

        self.assertIn("platform: linux/amd64", compose)
        self.assertIn(".:/workspace", compose)
        self.assertIn("claw-spice:local", compose)
        self.assertIn("8000:8000", compose)

    def test_host_wrapper_serves_docs_with_ports(self) -> None:
        wrapper = Path("claw-spice").read_text()

        self.assertIn("--service-ports", wrapper)
        self.assertIn("build-prebuilt", wrapper)


if __name__ == "__main__":
    unittest.main()
