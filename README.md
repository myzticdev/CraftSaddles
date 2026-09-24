# CraftSaddles

A Minecraft Java datapack by **myzticdev** that backports vanilla saddle crafting
to **1.13 through 1.21.5**. Three leather and one iron ingot produce **one saddle**
using an ordinary crafting table in Survival or Creative.

| | | |
| :---: | :---: | :---: |
| Empty | Leather | Empty |
| Leather | Iron ingot | Leather |
| Empty | Empty | Empty |

The two occupied rows may also be placed in the bottom two rows of the table.
The pattern is `" X "`, `"X#X"`, where `X` is leather and `#` is iron.
It was checked against `data/minecraft/recipe/saddle.json` in Mojang's 1.21.6
client archive. [Minecraft 1.21.6](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-6)
already includes saddle crafting, so this project has no releases for 1.21.6 or newer.

Only `craftsaddles:saddle` is added. There are no cooking recipes, functions,
tick loops, resource packs, loot changes, or recipe-unlock advancements. Place
ingredients manually; automatic recipe-book unlocking is not provided. Worlds
using `doLimitedCrafting` should leave it at its vanilla default, `false`.

## Downloads and compatibility

Choose **one** ZIP from [Releases](https://github.com/myzticdev/CraftSaddles/releases).
The initial release is pending manual gameplay testing.

| ZIP filename | Supported Java versions | Data pack format |
| --- | --- | --- |
| `CraftSaddles-1.13-1.13.2.zip` | 1.13–1.13.2 | 4 |
| `CraftSaddles-1.14-1.14.4.zip` | 1.14–1.14.4 | 4 |
| `CraftSaddles-1.15-1.16.1.zip` | 1.15–1.16.1 | 5 |
| `CraftSaddles-1.16.2-1.16.5.zip` | 1.16.2–1.16.5 | 6 |
| `CraftSaddles-1.17-1.17.1.zip` | 1.17–1.17.1 | 7 |
| `CraftSaddles-1.18-1.18.1.zip` | 1.18–1.18.1 | 8 |
| `CraftSaddles-1.18.2.zip` | 1.18.2 | 9 |
| `CraftSaddles-1.19-1.19.3.zip` | 1.19–1.19.3 | 10 |
| `CraftSaddles-1.19.4.zip` | 1.19.4 | 12 |
| `CraftSaddles-1.20-1.20.1.zip` | 1.20–1.20.1 | 15 |
| `CraftSaddles-1.20.2-1.21.5.zip` | 1.20.2–1.21.5 | 18–71 |

These are supported target ranges, not claims that every patch was played.
**No manual gameplay checks have been completed yet.** See [TESTING.md](TESTING.md)
and the exact-version [results record](tests/manual-results.json). Automated
validation checks data and packaging; it does not prove crafting or consumption
works in Minecraft. Snapshots and modded environments are outside the test scope.

## Installation and removal

1. Back up the world. Put the matching ZIP in `<world>/datapacks/`.
2. Reopen the world or run `/reload` with cheats or server operator permissions.
3. Check `/datapack list enabled` and craft using the pattern above.

Install only one CraftSaddles variant. If downloading
`CraftSaddles-myzticdev-All-Versions.zip`, extract it and install only the matching
inner ZIP. **Do not install the all-versions bundle itself.** No resource pack is needed.

To remove, close the world/server, remove the ZIP from `datapacks/`, then reopen.
Already crafted saddles remain normal vanilla items. Remove the pack before
upgrading a world to 1.21.6 or newer.

## Build and validate

Requires **Python 3.11+**, with no third-party dependencies. Git is required for
the clean-checkout check. From the repository root, the complete build command is:

```sh
python scripts/build.py
```

If Windows only provides the Python launcher, substitute `py -3.11` for `python`.
The build validates every source JSON and `pack.mcmeta`, supported ranges, all
effective overlay selections, exact recipe schemas and content, and archive roots.
Only after validation succeeds does it safely recreate this project's `dist/`.
Errors exit nonzero. ZIPs have sorted entries, fixed timestamps and permissions,
canonical UTF-8 JSON, and stored entries to avoid compression-library differences.
The build reopens output archives and checks integrity and exact contents.

Generated files in ignored `dist/`:

- The eleven individual ZIPs in the table above.
- `SHA256SUMS.txt`, covering those eleven ZIPs.
- `CraftSaddles-myzticdev-All-Versions.zip`, containing the eleven ZIPs and checksums.

Every datapack has `pack.mcmeta` and `data/` at its root. No icon has been supplied.
If one is supplied later, a shared `src/pack.png` is packaged at every datapack root.
Never modify generated files by hand.

```sh
python -m unittest discover -s scripts -p "test_*.py"
python scripts/build.py
# Commit all intended build inputs before comparing a clean checkout:
python scripts/check_reproducibility.py
```

The last command compares all thirteen output hashes over repeated builds and a
temporary local Git clone, and runs the regression suite in that clean checkout.
There is no dependency-install, lint, or separate compilation command.

## Maintaining compatibility

`src/targets.json` lists releases. `src/packs/<range>/pack.mcmeta` holds editable
metadata. Four shared definitions in `src/recipes/` cover the required crafting
schemas. `scripts/build.py` assembles these and independently checks their exact
shape, ingredients, result, permitted fields, and compatibility contracts.

The 1.13 variant uses `crafting_shaped`; the 1.14 variant uses the canonical
`minecraft:crafting_shaped` found in that version's vanilla recipes. Both use pack
format 4. Separate inputs preserve version-matched serializer forms; no smoker
behavior is involved. Later legacy splits follow data pack format changes.

The modern pack uses `pack_format: 18`, `supported_formats: 18–71`, and three
nonoverlapping overlays:

| Formats | Released versions | Recipe representation |
| --- | --- | --- |
| 18–40 (base) | 1.20.2–1.20.4 | `recipes/`, object ingredients, result `item` |
| 41–47 | 1.20.5–1.20.6 | `recipes/`, object ingredients, result `id` |
| 48–56 | 1.21–1.21.1 | `recipe/`, object ingredients, result `id` |
| 57–71 | 1.21.2–1.21.5 | `recipe/`, string ingredient keys, result `id` |

Each result explicitly has `count: 1`. Overlay intervals cover intervening format
numbers to keep selection continuous; this is not a snapshot-support claim.
Overlays replace matching paths and cannot delete old files. After the directory
rename, the base plural `recipes/` path remains in the ZIP but Minecraft ignores
it; validation checks that exactly one saddle recipe is effective.

Keep targets, metadata, validator contracts, tests, and documentation in agreement.
Do not introduce `min_format`/`max_format`, cooking overlays, or compatibility
beyond format 71. Technical details and primary references are in
[COMPATIBILITY.md](COMPATIBILITY.md).

## Testing and release

Pushes and pull requests run regression checks, validated builds, and clean-checkout
reproducibility through `.github/workflows/ci.yml`. CI uploads build artifacts.
Tagged releases run the same checks and extract the matching changelog entry.
The release script also requires every manual matrix row to pass with a matching
ZIP digest. Invalid tags, pending results, stale artifacts, or validation failures
prevent publication.

Before v1.0.0, complete [the manual matrix](TESTING.md), resolve failures, update
the dated 1.0.0 changelog entry with all shipped changes, inspect all public text
and archive contents, and run final checks. Prepare the result for review and
wait for explicit release authorization before creating/pushing `v1.0.0`.

Authorized maintenance releases use `vMAJOR.MINOR.PATCH` tags. The release workflow
uploads all thirteen generated files. After publication, verify the successful
Actions run, expected asset names, and all downloaded asset SHA-256 values against
the local build; also check `SHA256SUMS.txt` against the individual datapacks.

Publish under **myzticdev** only. Modrinth and CurseForge publishing are not
connected. Any future integration must use GitHub Actions secrets for tokens.
See [CONTRIBUTING.md](CONTRIBUTING.md) for permanent maintenance requirements.
