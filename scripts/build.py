"""Validate editable inputs and build deterministic CraftSaddles archives."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MASTER = 'CraftSaddles-myzticdev-All-Versions.zip'
DESCRIPTION = 'CraftSaddles by myzticdev - Craft 3 leather and 1 iron ingot into 1 saddle.'
TARGETS = [
    ('1.13-1.13.2', 4, 'plain'),
    ('1.14-1.14.4', 4, 'legacy'),
    ('1.15-1.16.1', 5, 'legacy'),
    ('1.16.2-1.16.5', 6, 'legacy'),
    ('1.17-1.17.1', 7, 'legacy'),
    ('1.18-1.18.1', 8, 'legacy'),
    ('1.18.2', 9, 'legacy'),
    ('1.19-1.19.3', 10, 'legacy'),
    ('1.19.4', 12, 'legacy'),
    ('1.20-1.20.1', 15, 'legacy'),
    ('1.20.2-1.21.5', 18, 'legacy'),
]
OVERLAYS = [('result_stack', 41, 47, 'stack'),
            ('singular_recipe', 48, 56, 'stack'),
            ('string_ingredients', 57, 71, 'strings')]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f'Invalid JSON constant: {value}')


def parse(data):
    return json.loads(data, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def expected_recipe(schema):
    require(schema in {'plain', 'legacy', 'stack', 'strings'}, 'Unknown recipe schema')
    return {
        'type': 'crafting_shaped' if schema == 'plain' else 'minecraft:crafting_shaped',
        'pattern': [' X ', 'X#X'],
        'key': {symbol: item if schema == 'strings' else {'item': item}
                for symbol, item in [('X', 'minecraft:leather'), ('#', 'minecraft:iron_ingot')]},
        'result': {'id' if schema in {'stack', 'strings'} else 'item': 'minecraft:saddle',
                   'count': 1},
    }


def check_recipe(recipe, schema):
    # Canonical comparison also rejects JSON booleans and floats used as counts.
    require(json.dumps(recipe, sort_keys=True) == json.dumps(expected_recipe(schema), sort_keys=True),
            f'Invalid saddle recipe or shaped crafting schema: {schema}')


def recipe_path(fmt):
    folder = 'recipe' if fmt >= 48 else 'recipes'
    return f'data/craftsaddles/{folder}/saddle.json'


def expected_meta(fmt, modern=False):
    meta = {'pack': {'pack_format': fmt, 'description': DESCRIPTION}}
    if modern:
        meta['pack']['supported_formats'] = {'min_inclusive': 18, 'max_inclusive': 71}
        meta['overlays'] = {'entries': [
            {'formats': {'min_inclusive': low, 'max_inclusive': high}, 'directory': directory}
            for directory, low, high, _ in OVERLAYS]}
    return meta


def effective_recipes(files, fmt, entries):
    effective = {name: content for name, content in files.items() if name.startswith('data/')}
    for entry in entries:
        bounds = entry['formats']
        if bounds['min_inclusive'] <= fmt <= bounds['max_inclusive']:
            prefix = entry['directory'] + '/'
            effective.update({name[len(prefix):]: content for name, content in files.items()
                              if name.startswith(prefix)})
    # After the directory rename the old plural directory is ignored by Minecraft.
    folder = '/recipe/' if fmt >= 48 else '/recipes/'
    return {name: content for name, content in effective.items() if folder in name}


def check_pack(files, target):
    name, fmt, schema = target
    modern = name == '1.20.2-1.21.5'
    meta = parse(files['pack.mcmeta'])
    require(meta == expected_meta(fmt, modern), f'Invalid compatibility metadata: {name}')
    expected = {'pack.mcmeta', recipe_path(fmt)}
    if 'pack.png' in files:
        expected.add('pack.png')
    check_recipe(parse(files[recipe_path(fmt)]), schema)
    if modern:
        for directory, low, _, overlay_schema in OVERLAYS:
            path = f'{directory}/{recipe_path(low)}'
            expected.add(path)
            check_recipe(parse(files[path]), overlay_schema)
        entries = meta['overlays']['entries']
        for current in range(18, 72):
            selected = [entry for entry in entries
                        if entry['formats']['min_inclusive'] <= current <= entry['formats']['max_inclusive']]
            require(len(selected) == (0 if current < 41 else 1), 'Overlay gap or overlap')
            effective = effective_recipes(files, current, entries)
            require(set(effective) == {recipe_path(current)}, f'Invalid effective recipes: {current}')
            current_schema = 'legacy' if current < 41 else 'stack' if current < 57 else 'strings'
            check_recipe(parse(effective[recipe_path(current)]), current_schema)
    require(set(files) == expected, f'Unexpected or missing pack files: {name}')


def archive(files):
    stream = io.BytesIO()
    # Stored entries avoid compression-library differences across platforms.
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as output:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            output.writestr(info, data)
    result = stream.getvalue()
    verify_archive(result, files)
    return result


def verify_archive(data, files):
    with zipfile.ZipFile(io.BytesIO(data)) as packed:
        require(packed.testzip() is None, 'ZIP integrity failure')
        require(packed.namelist() == sorted(files), 'Unexpected ZIP root structure or members')
        require(not packed.comment, 'Unexpected ZIP comment')
        for info in packed.infolist():
            require(packed.read(info.filename) == files[info.filename], 'ZIP content mismatch')
            require(info.date_time == (1980, 1, 1, 0, 0, 0), 'Unstable ZIP timestamp')
            require(info.create_system == 3 and info.external_attr == 0o100644 << 16,
                    'Unstable ZIP permissions')
            require(info.compress_type == zipfile.ZIP_STORED and not info.extra and not info.comment,
                    'Unexpected ZIP metadata')


def safe_tree(path):
    require(not path.is_symlink() and path.resolve() == path, f'Redirected path: {path.name}')
    if path.exists():
        require(path.is_dir(), f'Not a directory: {path.name}')
        for child in path.rglob('*'):
            require(not child.is_symlink() and child.resolve() == path / child.relative_to(path),
                    f'Redirected path in {path.name}')


def release_files(root=ROOT):
    src = root / 'src'
    safe_tree(src)
    expected_sources = {'targets.json'} | {f'recipes/{s}.json' for s in ('plain', 'legacy', 'stack', 'strings')}
    expected_sources.update(f'packs/{name}/pack.mcmeta' for name, _, _ in TARGETS)
    if (src / 'pack.png').exists():
        expected_sources.add('pack.png')
    require({p.relative_to(src).as_posix() for p in src.rglob('*') if p.is_file()} == expected_sources,
            'Unexpected or missing source files')
    # Parse every source JSON and mcmeta before emitting any output.
    inputs = {p.relative_to(src).as_posix(): parse(p.read_bytes())
              for p in src.rglob('*') if p.suffix in {'.json', '.mcmeta'}}
    require(inputs['targets.json'] == [dict(range=n, pack_format=f, schema=s) for n, f, s in TARGETS],
            'Invalid targets, version ranges, or schemas')
    for schema in ('plain', 'legacy', 'stack', 'strings'):
        check_recipe(inputs[f'recipes/{schema}.json'], schema)
    icon = {}
    if 'pack.png' in expected_sources:
        data = (src / 'pack.png').read_bytes()
        require(data.startswith(b'\x89PNG\r\n\x1a\n') and data[12:16] == b'IHDR', 'Invalid PNG icon')
        icon['pack.png'] = data
    releases = {}
    for target in TARGETS:
        name, fmt, schema = target
        files = {**icon, 'pack.mcmeta': encode(inputs[f'packs/{name}/pack.mcmeta']),
                 recipe_path(fmt): encode(inputs[f'recipes/{schema}.json'])}
        if name == '1.20.2-1.21.5':
            for directory, low, _, overlay_schema in OVERLAYS:
                files[f'{directory}/{recipe_path(low)}'] = encode(inputs[f'recipes/{overlay_schema}.json'])
        check_pack(files, target)
        releases[f'CraftSaddles-{name}.zip'] = archive(files)
    releases['SHA256SUMS.txt'] = ''.join(
        f'{hashlib.sha256(data).hexdigest()}  {name}\n' for name, data in sorted(releases.items())).encode()
    releases[MASTER] = archive(releases)
    return releases


def build(root=ROOT):
    require(sys.version_info >= (3, 11), 'Python 3.11 or newer is required')
    releases = release_files(root)
    dist = root / 'dist'
    require(root == root.resolve() and dist.resolve() == root / 'dist', 'Unsafe build root or dist')
    safe_tree(dist)
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    for name, data in releases.items():
        path = dist / name
        path.write_bytes(data)
        require(path.read_bytes() == data, f'Written output mismatch: {name}')
        if name.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as packed:
                members = {member: packed.read(member) for member in packed.namelist()}
            verify_archive(path.read_bytes(), members)
    print(f'Validated {len(TARGETS)} datapacks; wrote {len(releases)} release files to dist/.')


if __name__ == '__main__':
    try:
        build()
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        sys.exit(1)
