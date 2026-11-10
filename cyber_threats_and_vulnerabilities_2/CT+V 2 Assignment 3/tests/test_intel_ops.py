"""Offline functional and safety tests; no network or application imports."""
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import intel_ops as ops


class Response(io.BytesIO):
    status = 200
    def geturl(self):
        return ops.PUBLIC_SOURCES['apt38']


class FakeOpener:
    def __init__(self, body):
        self.body = body
    def open(self, request, timeout):
        if timeout != 12:
            raise AssertionError('Timeout changed')
        return Response(self.body)


class IntelOperations(unittest.TestCase):
    def setUp(self):
        self.now = ops.utc('2026-11-10T20:00:00Z')
        self.scenario = json.loads((ops.ROOT / 'tests/scenario.json').read_text())
        self.events = self.scenario['events']

    def test_reuses_prior_ledger_and_deduplicates(self):
        rows, records = ops.historical_indicators(self.now)
        self.assertEqual((len(rows), len(records)), (4, 2))

    def test_derivative_sources_do_not_inflate_confidence(self):
        _, records = ops.historical_indicators(self.now)
        self.assertTrue(all(r['independent_source_families'] == ['E02'] and r['confidence'] == 70 for r in records))

    def test_source_observation_date_is_not_refreshed(self):
        _, records = ops.historical_indicators(self.now)
        self.assertTrue(all(r['observed_at'].startswith('2026-08-27') for r in records))

    def test_historical_infrastructure_expires(self):
        _, records = ops.historical_indicators(self.now)
        self.assertEqual(next(r['state'] for r in records if r['type'] == 'url'), 'expired')

    def test_indicators_remain_defanged_and_non_enforcing(self):
        _, records = ops.historical_indicators(self.now)
        self.assertTrue(all(not r['enforcement_allowed'] and r['actor_attribution'] == 'unknown' for r in records))
        self.assertTrue(next(r['value'] for r in records if r['type'] == 'url').startswith('hxxp://'))

    def test_review_records_reason_without_mutating_evidence(self):
        _, records = ops.historical_indicators(self.now)
        record = next(r for r in records if r['type'] == 'sha256')
        result = ops.review_indicator(record, 'approve_hunt', 'Simulated analyst', 'Training-only exact hash hunt', self.now)
        self.assertEqual(result['state'], 'approved_for_hunt')
        self.assertEqual(len(result['review_history']), 1)
        self.assertNotIn('review_history', record)
        self.assertFalse(result['enforcement_allowed'])

    def test_expired_indicator_cannot_be_approved(self):
        _, records = ops.historical_indicators(self.now)
        with self.assertRaises(ValueError):
            ops.review_indicator(records[1], 'approve_hunt', 'Analyst', 'training', self.now)

    def test_false_positive_suppression(self):
        _, records = ops.historical_indicators(self.now)
        record = ops.review_indicator(records[0], 'false_positive', 'Analyst', 'Training disposition', self.now)
        with self.assertRaises(ValueError):
            ops.review_indicator(record, 'approve_hunt', 'Analyst', 'training', self.now)

    def test_revocation(self):
        _, records = ops.historical_indicators(self.now)
        record = ops.review_indicator(records[0], 'revoke', 'Analyst', 'Training source correction', self.now)
        self.assertEqual(record['state'], 'revoked')

    def test_review_requires_accountable_metadata(self):
        _, records = ops.historical_indicators(self.now)
        with self.assertRaises(ValueError):
            ops.review_indicator(records[0], 'revoke', '', '', self.now)

    def test_correlates_expected_campaign(self):
        mapped, alerts = ops.track(self.events)
        self.assertEqual(len(mapped), 9)
        self.assertEqual([a['host'] for a in alerts], ['demo-policy-01'])
        self.assertEqual({e['technique'] for e in mapped}, {t[0] for t in ops.TECHNIQUES.values()})

    def test_case_boundaries_are_preserved(self):
        events = deepcopy(self.events[:3]); events[2]['case'] = 'UNRELATED'
        self.assertEqual(ops.track(events)[1], [])

    def test_host_boundaries_are_preserved(self):
        events = deepcopy(self.events[:3]); events[2]['host'] = 'unrelated'
        self.assertEqual(ops.track(events)[1], [])

    def test_reversed_sequence_does_not_alert(self):
        events = deepcopy(self.events[1:3]); events[1]['time'] = '2026-11-10T12:01:00Z'
        self.assertEqual(ops.track(events)[1], [])

    def test_outside_window_does_not_alert(self):
        self.assertEqual(ops.track(self.events[-2:])[1], [])

    def test_duplicate_events_do_not_inflate_alerts(self):
        mapped, alerts = ops.track(self.events + self.events)
        self.assertEqual((len(mapped), len(alerts)), (9, 1))

    def test_conflicting_event_identifier_rejected(self):
        conflict = {**self.events[0], 'host': 'changed'}
        with self.assertRaises(ValueError): ops.track(self.events + [conflict])

    def test_unlabelled_real_telemetry_is_rejected(self):
        with self.assertRaises(ValueError): ops.track([{**self.events[0], 'simulation': False}])

    def test_timezone_required(self):
        with self.assertRaises(ValueError): ops.utc('2026-11-10T12:00:00')

    def test_controlled_benchmark(self):
        metrics = ops.benchmark(ops.track(self.events)[1], self.scenario['expected_hosts'])
        self.assertEqual((metrics['tp'], metrics['fp'], metrics['fn'], metrics['tn']), (1, 0, 0, 3))

    def test_benchmark_exposes_missed_and_false_alerts(self):
        result = ops.benchmark([{'host': 'negative'}], {'positive': True, 'negative': False})
        self.assertEqual((result['fp'], result['fn'], result['precision'], result['recall']), (1, 1, 0, 0))

    def test_cannot_write_outside_assignment(self):
        with self.assertRaises(ValueError): ops.confined(ops.REPO / 'outside-assignment')

    def test_redirects_fail_closed(self):
        with self.assertRaises(ValueError): ops.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.invalid')

    def test_collector_accepts_valid_bounded_json(self):
        body = b'{"name":"APT38 (G0082)","domain":"enterprise-attack","techniques":[{"techniqueID":"T1059.001"}]}'
        self.assertEqual(ops.fetch_public('apt38', FakeOpener(body)), body)

    def test_collector_rejects_wrong_actor_layer(self):
        body = b'{"name":"FIN7 (G0046)","domain":"enterprise-attack","techniques":[{"techniqueID":"T1059.001"}]}'
        with self.assertRaises(ValueError): ops.fetch_public('apt38', FakeOpener(body))

    def test_collector_rejects_malformed_technique_id(self):
        body = b'{"name":"APT38 (G0082)","domain":"enterprise-attack","techniques":[{"techniqueID":"invalid"}]}'
        with self.assertRaises(ValueError): ops.fetch_public('apt38', FakeOpener(body))

    def test_collector_rejects_oversized_response(self):
        with self.assertRaises(ValueError): ops.fetch_public('apt38', FakeOpener(b'x' * (ops.MAX_BYTES + 1)))

    def test_collector_rejects_malformed_json(self):
        with self.assertRaises(ValueError): ops.fetch_public('apt38', FakeOpener(b'not-json'))

    def test_collector_rejects_unknown_source(self):
        with self.assertRaises(KeyError): ops.fetch_public('https://example.invalid')

    def test_historical_write_finding_is_not_currently_reasserted(self):
        findings = ops.reconcile_findings()
        record = next(f for f in findings if f['id'] == 'DVI-POLICY-WRITE')
        self.assertEqual(record['disposition'], 'superseded_in_newer_isolated_tests')
        self.assertNotIn('closed', record['disposition'])

    def test_full_offline_run_and_collision_protection(self):
        with tempfile.TemporaryDirectory(dir=ops.ROOT / 'evidence') as temp:
            out = Path(temp) / 'run'
            _, metrics = ops.run(output=out, as_of=self.now.isoformat())
            self.assertEqual(metrics['collection_verified'], 0)
            self.assertEqual(metrics['unique_indicators'], 2)
            self.assertEqual(len(json.loads((out / 'campaigns.json').read_text())), 3)
            with self.assertRaises(FileExistsError): ops.run(output=out)

    def test_collection_failure_is_visible_without_fabricated_success(self):
        with tempfile.TemporaryDirectory(dir=ops.ROOT / 'evidence') as temp, patch.object(ops, 'fetch_public', side_effect=OSError('offline fixture')):
            out, metrics = ops.run(collect=True, output=Path(temp) / 'run')
            self.assertEqual((metrics['collection_verified'], metrics['collection_blocked']), (0, 3))
            self.assertTrue(all(c['status'] == 'BLOCKED' for c in json.loads((out / 'collection.json').read_text())))


if __name__ == '__main__':
    unittest.main(verbosity=2)
