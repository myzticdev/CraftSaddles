# Compatibility reference

The saddle pattern was read directly from Mojang's
[1.21.6 client archive](https://piston-data.mojang.com/v1/objects/740a125b83dd3447feaa3c5e891ead7fbb21ae28/client.jar),
at `data/minecraft/recipe/saddle.json`. Its shape is `[" X ", "X#X"]`,
with `X = minecraft:leather`, `# = minecraft:iron_ingot`, and result
`{"count": 1, "id": "minecraft:saddle"}`. The optional vanilla category is
`equipment`; this backport omits category to share the minimum necessary fields.

Client downloads were resolved through Mojang's
[version manifest](https://piston-meta.mojang.com/mc/game/version_manifest_v2.json)
and checked against their advertised SHA-1 before reading recipe JSON. These are
data checks, not gameplay tests.

| Version | Inspected vanilla shaped recipe | Client object SHA-1 | Finding |
| --- | --- | --- | --- |
| 1.13 | `data/minecraft/recipes/leather_helmet.json` | `c0b970952cdd279912da384cdbfc0c26e6c6090b` | Plain `crafting_shaped`, object key, result `item` |
| 1.14 | `data/minecraft/recipes/leather_helmet.json` | `7a762a59345c13af7d87111207a93f5a8607f6c0` | Namespaced serializer, format 4 |
| 1.20.4 | `data/minecraft/recipes/leather_helmet.json` | `fd19469fed4a4b4c15b2d5133985f0e3e7816a8a` | Object key, result `item`, format 26 |
| 1.20.5 | `data/minecraft/recipes/leather_helmet.json` | `c6b92b2374a629f20802bb284f98a4ee790e950a` | Result `id` and count, format 41 |
| 1.21 | `data/minecraft/recipe/leather_helmet.json` | `0e9a07b9bb3390602f977073aa12884a4ce12431` | Singular directory, format 48 |
| 1.21.2 | `data/minecraft/recipe/leather_helmet.json` | `c7ac2d0d86f4ca416cab9064ff8a281852ad0c7b` | String key values, format 57 |
| 1.21.5 | `data/minecraft/recipe/leather_helmet.json` | `b88808bbb3da8d9f453694b5d8f74a3396f1a533` | Same relevant crafting schema, format 71 |
| 1.21.6 | `data/minecraft/recipe/saddle.json` | `740a125b83dd3447feaa3c5e891ead7fbb21ae28` | Exact saddle pattern; outside backport support |

For each object hash above, the official client URL is
`https://piston-data.mojang.com/v1/objects/<hash>/client.jar`.

Official technical references:

- [1.20.2](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-20-2):
  format 18, `supported_formats`, inclusive overlay ranges, replacement semantics.
- [1.20.5](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-20-5):
  format 41 and crafting result item stacks.
- [1.21](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21):
  format 48 and `recipes` to `recipe` rename.
- [1.21.2](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-2):
  format 57 and simplified recipe ingredients, including shaped key values.
- [1.21.5](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-5):
  format 71, the upper bound for this project.
- [1.21.6](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-6):
  vanilla saddle crafting introduced.

The 1.13 and 1.14 artifacts intentionally follow each version's vanilla serializer
spelling. Do not interpret their shared pack format as proof of identical schemas.
Namespaced serializer rejection in 1.13 is a regression risk. The separate 1.14
definition uses its canonical namespaced identifier; this does not claim that all
later parsers reject omitted default namespaces.
