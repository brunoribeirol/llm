# Tool Policy

## Routing principle
Use the smallest capability that can answer the question reliably:

1. repository instructions and manifests;
2. native file search;
3. native code intelligence/LSP;
4. structural search (`ast-grep`/`sg`) when syntax matters;
5. external documentation (Context7) when current library behavior is required;
6. symbolic navigation (Serena) when native intelligence is insufficient;
7. architecture graph (Graphify) only for broad, large-repository questions;
8. Vault retrieval (QMD) only for curated external memory.

Do not activate tools simply because they are installed.

## Context7
Use only to verify current third-party library/framework documentation. Do not use it for local-code discovery.

## Serena
Use for symbol definitions, references, callers, and cross-file refactors only when configured and it materially improves over native code intelligence.

## Graphify
Use only for broad architecture questions in large repositories. Generate lazily, reuse a fresh graph, keep generated caches out of Git, and never enable a global watch/commit hook automatically.

## QMD
Use only for semantic retrieval from the configured Obsidian Vault. QMD indexing is explicit opt-in. Agent Workspace blocks QMD <=2.6.3 and unknown versions for mutating/search integration because project-local `.qmd` trust issues were reported in 2.6.3. Use only the dedicated `agent-workspace-vault` index, run QMD from outside arbitrary repositories, read snippets first, and open full notes only when needed.

## ast-grep
Use for syntax-aware search/refactor discovery when text search is ambiguous. Search first; do not perform repository-wide rewrites without review.

## Gitleaks
Use for explicit security/release scans. Do not run on every edit and never echo discovered secret values into reports or Vault notes.

## RTK
Use only for known verbose commands. If compression hides evidence or a command behaves unexpectedly, repeat the raw command.

## ccusage
Optional observability only. Use to compare real usage trends across sessions/agents; it is not a runtime dependency or a reason to impose model-specific hacks.

## External tool installation
Hooks never install or update tools. Use `agent-workspace tools-recommend` to see what may help, then review and install explicitly. Prefer native/CLI capabilities over a permanent MCP when both solve the same task.
