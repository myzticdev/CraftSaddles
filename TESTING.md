# Gameplay testing

All twenty versions in the matrix below were reported tested and confirmed by
the maintainer on **2026-09-24**, covering the requested gameplay procedure.
The results are maintainer-reported confirmations, not automated gameplay tests.
The exact versions, checks, and matching build digests are recorded in
`tests/manual-results.json`. No pack enablement, JSON validation, or archive
inspection alone is counted as a successful crafting test.

The supplied pack icon was added after those confirmations. On 2026-09-24,
myzticdev explicitly accepted this icon-only change without repeating gameplay
tests and authorized v1.0.0 publication. Reconstructing each ZIP without pack.png
reproduced its original tested SHA-256, verifying unchanged recipes and metadata.
The original hashes are retained as `tested_artifact_sha256`; `artifact_sha256`
identifies the final accepted ZIP. Each row records the packaging acceptance.

Use unmodified Minecraft Java in Prism. Test one row at a time, using a fresh
Creative world with cheats enabled and only the matching CraftSaddles ZIP.
Versions at both sides of the modern schema transitions are included.

| Minecraft version | ZIP suffix (`CraftSaddles-<suffix>.zip`) | Coverage |
| --- | --- | --- |
| 1.13 | 1.13-1.13.2 | Earliest supported serializer |
| 1.13.2 | 1.13-1.13.2 | Last 1.13 patch |
| 1.14 | 1.14-1.14.4 | Namespaced serializer, same pack format |
| 1.16.1 | 1.15-1.16.1 | Format 5 |
| 1.16.5 | 1.16.2-1.16.5 | Format 6 |
| 1.17.1 | 1.17-1.17.1 | Format 7 |
| 1.18.1 | 1.18-1.18.1 | Format 8 |
| 1.18.2 | 1.18.2 | Format 9 |
| 1.19.3 | 1.19-1.19.3 | Format 10 |
| 1.19.4 | 1.19.4 | Format 12 |
| 1.20.1 | 1.20-1.20.1 | Last legacy ZIP, format 15 |
| 1.20.2 | 1.20.2-1.21.5 | Ranged metadata begins, format 18 |
| 1.20.4 | 1.20.2-1.21.5 | Before result-stack change, format 26 |
| 1.20.5 | 1.20.2-1.21.5 | Result-stack overlay, format 41 |
| 1.20.6 | 1.20.2-1.21.5 | Before directory rename, format 41 |
| 1.21 | 1.20.2-1.21.5 | Singular directory overlay, format 48 |
| 1.21.1 | 1.20.2-1.21.5 | Before ingredient change, format 48 |
| 1.21.2 | 1.20.2-1.21.5 | String ingredient overlay, format 57 |
| 1.21.4 | 1.20.2-1.21.5 | Format 61 |
| 1.21.5 | 1.20.2-1.21.5 | Maximum supported format 71 |

## Procedure for each row

1. Select the exact Minecraft release in Prism. Create a fresh vanilla Creative
   world with cheats enabled. Save and quit.
2. Place the specified ZIP from `dist/` in that world's `datapacks/` directory.
   Reopen the world and run `/reload`, then `/datapack list enabled`. Confirm the
   matching CraftSaddles filename is enabled and check for recipe errors.
3. Place a crafting table in Creative. Arrange leather at top-center, middle-left,
   and middle-right, with an iron ingot at middle-center. All other slots are empty.
   Confirm the output displays exactly **one saddle**. Take it once in Creative
   to check ordinary crafting, then clear the table and your inventory.
4. Prepare exactly 6 leather and 2 iron ingots. Run `/gamemode survival` and place
   2 leather in each of the three leather slots, plus 2 iron ingots in the center.
   Take one saddle normally. Verify one ingredient remains in each occupied slot:
   total consumption **3 leather + 1 iron**, output **1 saddle**. Take the second
   saddle and verify all four slots are empty.
5. With fresh ingredients in Survival, put three leather across the top row and
   one iron in the center of the second row. Confirm **no saddle output**. Also
   remove the iron from the correct pattern and confirm no saddle output.
6. Clear the table/inventory, prepare 12 leather and 4 iron ingots, and remain in
   Survival. Put 4 leather in each leather slot and 4 iron in the iron slot.
   Shift-click the output with enough free inventory slots. Expect **4 saddles**,
   all **12 leather + 4 iron** consumed, and no ingredients remaining. If the
   version takes one saddle at a time, repeat four times and report that behavior.
7. Confirm the enabled pack, Creative output, Survival consumption, incorrect
   pattern rejection, and batch quantities with the exact Minecraft version.
   Also report any red messages or unexpected behavior. Do not mark a whole row
   passed from a partial confirmation.

For convenient Survival supplies after clearing your inventory, use
`/give @s minecraft:leather 6` and `/give @s minecraft:iron_ingot 2` for step 4;
use counts 12 and 4 for step 6. Saddles do not stack, so leave four inventory slots.

## Recording and investigating

`tests/manual-results.json` is the release record. Each confirmation must include
the exact version, ZIP, date, individual checks, notes, and ZIP SHA-256 from that
build's `SHA256SUMS.txt`. Keep unknown checks `null` and status `pending`; use
`failed` for known failures. Record limitations in notes. Never infer success.

On failure, preserve Prism's Minecraft console and the instance's
`.minecraft/logs/latest.log`, identify recipe/pack errors, compare against the
same version's vanilla JSON, fix `src/` or tooling, rebuild, and retest affected
rows. A modified ZIP needs new gameplay confirmations and a new digest. Do not
edit generated ZIPs. The release gate checks every recorded digest against the
current build.

After all agreed rows pass, update this document and README's testing status,
date the changelog, rerun regression/build/reproducibility checks, inspect public
text and archive contents, and prepare v1.0.0 for explicit release approval.
