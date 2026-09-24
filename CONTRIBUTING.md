# Maintaining CraftSaddles

- Public developer: **myzticdev**. Project: **CraftSaddles**. Namespace: `craftsaddles`.
- Use ordinary maintenance language focused on functionality throughout source,
  comments, docs, commits, workflows, manifests, release notes, listings, and artifacts.
  Do not add development-assistant attribution, automated-authorship references,
  provenance notes, signatures, watermarks, or hidden attribution.
- Inspect repository instructions and existing tooling before changing anything.
  Preserve unrelated work and never expose or commit credentials.
- Add only the shaped saddle recipe. No cooking recipes, functions, tick loops,
  resource pack, loot changes, or recipe-unlock advancements.
- Support Java 1.13 through 1.21.5 only. Vanilla provides saddle crafting from
  1.21.6 onward; do not publish variants or extend support to those versions.
- Edit `src/` and tooling; never edit or commit `dist/`. Keep caches, temporary
  files, editor configuration, and machine-specific files out of Git.
- Keep shared recipe definitions in `src/recipes/` and metadata in `src/packs/`.
  Change targets, validator boundaries, documentation, and regression tests together.
  Verify schemas against version-matched vanilla data and official technical notes.
- Preserve the exact vanilla shape and quantities. Keep 1.13's plain serializer
  and later canonical namespaced serializers covered by regression tests.
- Use Python 3.11+ and the standard library. Run the regression suite and build;
  after committing inputs, run the repeated-build and clean-checkout check.
- Keep supported ranges separate from actual gameplay results. Record only
  explicit test confirmations, exact Minecraft versions, checks, dates, and the
  tested ZIP's SHA-256 in `tests/manual-results.json`. Retest changed artifacts.
- Before v1.0.0, complete the manual matrix, resolve failures, include every shipped
  change in the changelog, run final checks, and inspect all public text and ZIP contents.
- Prepare changes for review and wait for explicit release authorization before
  pushing a release tag. After publication, verify Actions, all thirteen assets,
  and every asset's SHA-256 against the local build.
- Modrinth and CurseForge are not connected. Any future publishing integration
  requires separate implementation and verification. Store tokens only in GitHub
  Actions secrets, never in chat, source, or generated files.
- If supplied, preserve the original icon artwork, visually verify conversion to
  `src/pack.png`, and check its inclusion at each datapack root. Do not invent an icon.
