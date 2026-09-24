"""Regression checks for shaped recipes, overlay boundaries, and release archives."""
import copy
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

import build


class RecipeTests(unittest.TestCase):
    def recipe(self, schema):
        return build.parse((build.ROOT / f'src/recipes/{schema}.json').read_bytes())

    def test_serializer_boundary(self):
        for schema in ('plain', 'legacy'):
            recipe = self.recipe(schema)
            build.check_recipe(recipe, schema)
            recipe['type'] = ('minecraft:crafting_shaped' if schema == 'plain' else 'crafting_shaped')
            with self.assertRaises(ValueError):
                build.check_recipe(recipe, schema)

    def test_schema_boundaries(self):
        for schema in ('plain', 'legacy', 'stack', 'strings'):
            for other in ('plain', 'legacy', 'stack', 'strings'):
                with self.subTest(schema=schema, other=other):
                    if schema == other:
                        build.check_recipe(self.recipe(other), schema)
                    else:
                        with self.assertRaises(ValueError):
                            build.check_recipe(self.recipe(other), schema)

    def test_wrong_shapes_ingredients_counts_and_extra_content(self):
        original = self.recipe('strings')
        mutations = [
            ('pattern', ['XXX', ' # ']), ('pattern', ['X X', 'X# ']),
            ('pattern', ['X#X', ' X ']), ('pattern', [' X ', 'XXX']),
            ('key', {'X': 'minecraft:rabbit_hide', '#': 'minecraft:iron_ingot'}),
            ('key', {'X': ['minecraft:leather'], '#': 'minecraft:iron_ingot'}),
            ('key', {'X': 'minecraft:leather', '#': '#minecraft:iron_ingots'}),
            ('result', {'id': 'minecraft:saddle', 'count': 2}),
            ('result', {'id': 'minecraft:saddle', 'count': True}),
            ('result', {'id': 'minecraft:saddle', 'count': 1.0}),
            ('result', {'id': 'minecraft:leather', 'count': 1}),
            ('type', 'minecraft:crafting_shapeless'), ('group', 'extra'),
        ]
        for key, value in mutations:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                changed = copy.deepcopy(original)
                changed[key] = value
                build.check_recipe(changed, 'strings')

    def test_json_object_order_is_not_significant(self):
        recipe = self.recipe('strings')
        build.check_recipe(dict(reversed(list(recipe.items()))), 'strings')

    def test_strict_json(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{oops}'):
            with self.assertRaises(ValueError):
                build.parse(text)


class PackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.releases = build.release_files()
        with zipfile.ZipFile(io.BytesIO(cls.releases['CraftSaddles-1.20.2-1.21.5.zip'])) as packed:
            cls.modern = {name: packed.read(name) for name in packed.namelist()}

    def test_effective_transition_recipes(self):
        entries = build.parse(self.modern['pack.mcmeta'])['overlays']['entries']
        for fmt, schema in [(18, 'legacy'), (26, 'legacy'), (40, 'legacy'), (41, 'stack'),
                            (47, 'stack'), (48, 'stack'), (56, 'stack'), (57, 'strings'),
                            (61, 'strings'), (71, 'strings')]:
            with self.subTest(fmt=fmt):
                effective = build.effective_recipes(self.modern, fmt, entries)
                self.assertEqual(set(effective), {build.recipe_path(fmt)})
                build.check_recipe(build.parse(effective[build.recipe_path(fmt)]), schema)

    def test_overlay_gaps_overlap_future_ranges_and_bad_paths_fail(self):
        for mutation in ('gap', 'overlap', 'future', 'path', 'new_fields'):
            files = dict(self.modern)
            meta = build.parse(files['pack.mcmeta'])
            if mutation == 'gap':
                meta['overlays']['entries'][0]['formats']['min_inclusive'] = 42
            elif mutation == 'overlap':
                meta['overlays']['entries'][0]['formats']['max_inclusive'] = 48
            elif mutation == 'future':
                meta['pack']['supported_formats']['max_inclusive'] = 80
            elif mutation == 'path':
                meta['overlays']['entries'][0]['directory'] = '../outside'
            else:
                meta['pack']['min_format'] = 18
            files['pack.mcmeta'] = build.encode(meta)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                build.check_pack(files, build.TARGETS[-1])

    def test_missing_or_extra_pack_content_fails(self):
        required = [name for name in self.modern if name != 'pack.png']
        for name in required + ['data/craftsaddles/advancement/unlock.json']:
            files = dict(self.modern)
            if name in files:
                del files[name]
            else:
                files[name] = b'{}'
            with self.subTest(name=name), self.assertRaises((ValueError, KeyError)):
                build.check_pack(files, build.TARGETS[-1])

    def test_checksums_bundle_and_repeated_builds(self):
        self.assertEqual(self.releases, build.release_files())
        sums = self.releases['SHA256SUMS.txt'].decode().splitlines()
        self.assertEqual(len(sums), 11)
        for line in sums:
            digest, name = line.split('  ')
            self.assertEqual(digest, hashlib.sha256(self.releases[name]).hexdigest())
        build.verify_archive(self.releases[build.MASTER],
                             {n: d for n, d in self.releases.items() if n != build.MASTER})

    def test_invalid_source_preserves_existing_dist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            shutil.copytree(build.ROOT / 'src', root / 'src')
            (root / 'dist').mkdir()
            marker = root / 'dist/keep.txt'
            marker.write_text('keep')
            (root / 'src/recipes/plain.json').write_text('{}')
            with self.assertRaises(ValueError):
                build.build(root)
            self.assertEqual(marker.read_text(), 'keep')

    def test_redirected_dist_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            shutil.copytree(build.ROOT / 'src', root / 'src')
            outside = root / 'outside'
            outside.mkdir()
            marker = outside / 'keep.txt'
            marker.write_text('keep')
            try:
                (root / 'dist').symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('Directory symlinks require OS permission')
            with self.assertRaises(ValueError):
                build.build(root)
            self.assertEqual(marker.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
