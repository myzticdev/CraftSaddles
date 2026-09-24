# Changelog

## [1.0.0] - Unreleased

- Backport the vanilla shaped saddle recipe: three leather and one iron ingot
  produce one saddle in Minecraft Java 1.13 through 1.21.5.
- Provide ten legacy datapacks and one modern ranged datapack, with result-stack,
  recipe-directory, and ingredient-schema overlays ending at data pack format 71.
- Add strict source, recipe, metadata, overlay, and archive validation using
  Python 3.11+ and the standard library.
- Generate reproducible ZIPs, individual SHA-256 checksums, and an all-versions bundle.
- Add compatibility regression tests and repeated-build/clean-checkout verification.
- Add installation and maintenance documentation, a manual gameplay test matrix,
  push/pull-request CI, and tagged releases gated on matching gameplay results.

Release pending completion of the manual test matrix and release authorization.
