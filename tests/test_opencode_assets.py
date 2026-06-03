from __future__ import annotations

import json
import unittest
from pathlib import Path


class OpenCodeAssetTests(unittest.TestCase):
    def test_opencode_config_is_valid_json_and_registers_skills(self) -> None:
        config = json.loads(Path(".opencode/opencode.json").read_text())

        self.assertEqual(config["$schema"], "https://opencode.ai/config.json")
        self.assertEqual(config["skills"]["paths"], [".opencode/skills"])
        self.assertIn("show-schematic", config["command"])
        self.assertIn("template", config["command"]["test"])

    def test_all_skills_have_frontmatter_and_workflow_rules(self) -> None:
        skill_files = sorted(Path(".opencode/skills").glob("*/SKILL.md"))

        self.assertGreaterEqual(len(skill_files), 8)
        for skill_file in skill_files:
            text = skill_file.read_text()
            self.assertTrue(text.startswith("---\n"), skill_file)
            self.assertIn("name:", text, skill_file)
            self.assertIn("description:", text, skill_file)
            self.assertIn("OpenCode Rule", text, skill_file)

    def test_agents_are_subagents_with_permissions(self) -> None:
        agent_files = sorted(Path(".opencode/agent").glob("*.md"))

        self.assertGreaterEqual(len(agent_files), 5)
        for agent_file in agent_files:
            text = agent_file.read_text()
            self.assertIn("mode: subagent", text, agent_file)
            self.assertIn("permission:", text, agent_file)


if __name__ == "__main__":
    unittest.main()
