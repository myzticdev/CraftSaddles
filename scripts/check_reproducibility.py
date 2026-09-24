"""Compare repeated builds and an isolated clean checkout with the current build."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run_build(root):
    subprocess.run([sys.executable, str(root / 'scripts/build.py')], cwd=root, check=True)
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (root / 'dist').iterdir()}


def main():
    first = run_build(ROOT)
    if run_build(ROOT) != first:
        raise ValueError('Repeated builds differ')
    with tempfile.TemporaryDirectory(prefix='craftsaddles-checkout-') as directory:
        checkout = Path(directory) / 'checkout'
        subprocess.run(['git', '-c', f'safe.directory={ROOT.as_posix()}', 'clone', '--quiet',
                        '--no-hardlinks', str(ROOT), str(checkout)], check=True)
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_*.py'],
                       cwd=checkout, check=True)
        if run_build(checkout) != first:
            raise ValueError('Clean checkout differs; commit all build inputs before this check')
    print('Repeated builds and clean checkout match byte-for-byte (all 13 outputs).')


if __name__ == '__main__':
    main()
