# Installation and agent adapters

GraphLatch uses a portable `SKILL.md` bundle. Install the **entire** `skill/graph-latch` directory so the skill keeps its protocol reference and templates beside it.

## Claude Code

Project-local installation:

```bash
mkdir -p .claude/skills
cp -R /path/to/GraphLatch/skill/graph-latch .claude/skills/
```

Then start Claude Code in the project and invoke:

```text
/graph-latch
```

Claude Code project skills are stored in `.claude/skills/<skill-name>/SKILL.md`. See the [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

## Codex

Project-local installation:

```bash
mkdir -p .agents/skills
cp -R /path/to/GraphLatch/skill/graph-latch .agents/skills/
```

Then ask Codex to use the `graph-latch` skill for the task. Codex uses the Agent Skills format and project-level `.agents/skills/` directories. See [OpenAI's skills documentation](https://developers.openai.com/api/docs/guides/tools-skills) and [Codex skill installation guidance](https://developers.openai.com/api/reference/cli).

## OpenCode

Project-local installation:

```bash
mkdir -p .opencode/skills
cp -R /path/to/GraphLatch/skill/graph-latch .opencode/skills/
```

Then mention `@graph-latch` in your request, or ask the agent to load the skill by name. OpenCode also supports `.agents/skills/` and `.claude/skills/` compatibility paths. See [OpenCode Agent Skills](https://opencode.ai/docs/skills/).

## Other agents

If an agent supports Agent Skills, copy `skill/graph-latch` into its documented project or user skill directory. If it only supports persistent instruction files (for example `AGENTS.md`), you can add a short pointer instructing the agent to read `SKILL.md` when handling substantial multi-step work. Confirm the agent's documented discovery and invocation behaviour; do not assume every tool uses the same path or command syntax.

## User-level installation

The same directory can be copied into the agent's documented user-level skill directory to make it available across projects. Use the exact path documented by the agent and avoid maintaining multiple conflicting copies.

## Updating

When updating GraphLatch, replace the installed `graph-latch` folder as a unit. Keep project-local templates and run records under version control only when they are useful to the project; do not copy secrets or sensitive operational data into them.
