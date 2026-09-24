"""Release guard regressions."""
import hashlib
import unittest
from unittest.mock import patch

import release_notes


class ReleaseTests(unittest.TestCase):
    def test_rejects_invalid_tags(self):
        for tag in ('v1', 'v1.0', '1.0.0', 'v1.0.0-beta', 'v1.0.0\n', 'v1.0.0;echo'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release_notes.release_notes(tag)

    def test_missing_entry_fails(self):
        with self.assertRaisesRegex(ValueError, 'No changelog entry'):
            release_notes.release_notes('v999.0.0')

    def test_pending_manual_matrix_blocks_release(self):
        original = release_notes.parse

        def pending(data):
            record = original(data)
            record[0]['status'] = 'pending'
            return record

        with patch.object(release_notes, 'parse', side_effect=pending):
            with self.assertRaisesRegex(ValueError, 'Manual check pending'):
                release_notes.release_notes('v1.0.0')

    def test_stale_digest_blocks_release(self):
        original = release_notes.parse

        def stale(data):
            record = original(data)
            for row in record:
                row.update(status='passed', date='2026-09-24', notes='Test fixture', artifact_sha256='0' * 64)
                row['checks'] = {check: True for check in row['checks']}
            return record

        with patch.object(release_notes, 'parse', side_effect=stale):
            with self.assertRaisesRegex(ValueError, 'Tested artifact differs'):
                release_notes.release_notes('v1.0.0')

    def test_undated_changelog_blocks_release(self):
        original = release_notes.parse

        def completed(data):
            record = original(data)
            files = release_notes.release_files()
            for row in record:
                row.update(status='passed', date='2026-09-24', notes='Test fixture',
                           artifact_sha256=hashlib.sha256(files[row['zip']]).hexdigest())
                row['checks'] = {check: True for check in row['checks']}
            return record

        changelog = '# Changelog\n\n## [1.0.0] - Unreleased\n\nTest release.\n'
        with patch.object(release_notes, 'parse', side_effect=completed), \
                patch.object(release_notes.Path, 'read_text', return_value=changelog):
            with self.assertRaisesRegex(ValueError, 'must be dated'):
                release_notes.release_notes('v1.0.0')


if __name__ == '__main__':
    unittest.main()
