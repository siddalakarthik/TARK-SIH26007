import copy
import csv
import json
import math
from pathlib import Path
import random
import tempfile
import unittest
import contextlib
import io
from unittest.mock import patch
import numpy as np
from src.model import Parameters, components, speed_cap, operating_point, encounter, requirements, normalized_cycle
from src.experiments import validate_design, read_csv, write_csv
from src.verify import root_bisection, percentile, close, verify_numbers, verify_hashes

ROOT=Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def setUp(self): self.p=Parameters(1.5,1.5,2,1)
    def test_equation(self): self.assertAlmostEqual(components(5,self.p)['required_perception_range_m'],113/6)
    def test_conversion(self): self.assertEqual(operating_point(100,5,self.p)['speed_kmph'],18)
    def test_inverse(self):
        for r in [0,1,2,3,3.0000001,4,5,20,150,10000]:
            self.assertAlmostEqual(speed_cap(r,self.p),root_bisection(r,1.5,1.5,2,1),places=8)
    def test_boundary(self):
        self.assertEqual(speed_cap(3,self.p),0);self.assertGreater(speed_cap(3+1e-7,self.p),0)
        self.assertLess(operating_point(2,5,self.p)['safety_margin_m'],0)
    def test_zero_speed(self): self.assertEqual(components(0,self.p)['required_perception_range_m'],3)
    def test_zero_delay_extreme_deceleration(self):
        for a in [1e-9,1e9]:
            p=Parameters(0,a,2,1)
            self.assertAlmostEqual(speed_cap(20,p)/math.sqrt(34*a),1)
    def test_exact_requirement_epsilon(self):
        r=components(5,self.p)['required_perception_range_m']
        self.assertAlmostEqual(speed_cap(r,self.p),5)
        self.assertLess(speed_cap(r-1e-7,self.p),5);self.assertGreater(speed_cap(r+1e-7,self.p),5)
    def test_required_range_monotonic(self):
        for v in range(20):
            a=components(v,self.p)['required_perception_range_m']
            self.assertGreater(components(v+1,self.p)['required_perception_range_m'],a)
            self.assertGreaterEqual(components(v,Parameters(2,1.5,2,1))['required_perception_range_m'],a)
    def test_invalid_parameters(self):
        for x in [True,-1,float('nan'),float('inf'),'2']:
            with self.subTest(x=x),self.assertRaises(ValueError): Parameters(x,1,1,1)
        with self.assertRaises(ValueError):Parameters(1,0,1,1)
    def test_invalid_input(self):
        for x in [-1,float('nan'),float('inf'),True]:
            with self.subTest(x=x),self.assertRaises(ValueError):speed_cap(x,self.p)
    def test_monotonicity(self):
        rng=random.Random(26007)
        for _ in range(500):
            r=rng.uniform(1,150);p=Parameters(rng.uniform(0,5),rng.uniform(.1,5),rng.uniform(0,5),rng.uniform(0,5));v=speed_cap(r,p)
            self.assertLessEqual(speed_cap(r/2,p),v)
            self.assertLessEqual(speed_cap(r,Parameters(p.delay_s+1,p.deceleration_mps2,p.margin_m,p.uncertainty_m)),v)
            self.assertLessEqual(speed_cap(r,Parameters(p.delay_s,p.deceleration_mps2/2,p.margin_m,p.uncertainty_m)),v)
            self.assertLessEqual(speed_cap(r,Parameters(p.delay_s,p.deceleration_mps2,p.margin_m,p.uncertainty_m+1)),v)
    def test_age(self):
        caps=[operating_point(20,10,self.p,age_s=a)['speed_mps'] for a in [0,.25,1,1.0001]]
        self.assertEqual(caps,sorted(caps,reverse=True));self.assertEqual(caps[-1],0)
    def test_missing(self): self.assertEqual(operating_point(100,5,self.p,available=False)['speed_mps'],0)
    def test_margin_at_cap(self):
        for r in range(4,151): self.assertGreaterEqual(operating_point(r,15,self.p)['safety_margin_m'],-1e-8)
    def test_stationary(self):
        e=encounter(40,5,0,20,self.p,5)
        self.assertAlmostEqual(e['minimum_clearance_m'],20-5*1.5-25/3)
        self.assertAlmostEqual(e['detection_wait_s'],4)
    def test_encounter_independent_grid(self):
        # Independently integrate dense kinematics and check against exact extremum.
        for target in [-5,0,2.5,8]:
            e=encounter(20,5,target,20,self.p,5);t=np.linspace(0,1.5+5/1.5+5,40001)
            own=np.where(t<=1.5,5*t,np.where(t<=1.5+5/1.5,7.5+5*(t-1.5)-.75*(t-1.5)**2,7.5+25/3))
            self.assertAlmostEqual(float(np.min(20+target*t-own)),e['minimum_clearance_m'],places=6)
    def test_oncoming_limit(self): self.assertTrue(encounter(80,2,-2,50,self.p,5)['eventual_oncoming_collision'])
    def test_no_detection(self): self.assertFalse(encounter(40,2,3,20,self.p,5)['detected'])
    def test_inverse_requirements(self):
        r=components(5,self.p)['required_perception_range_m'];q=requirements(5,r,self.p)
        self.assertAlmostEqual(q['max_response_delay_s'],1.5);self.assertAlmostEqual(q['min_effective_deceleration_mps2'],1.5)
    def test_infeasible_requirement(self): self.assertIsNone(requirements(15,3,self.p)['max_response_delay_s'])
    def test_cycle(self):
        self.assertAlmostEqual(normalized_cycle(.4,.3,.3,5,2.5,5,.25)['normalized_cycle_time'],1.3)
        self.assertAlmostEqual(normalized_cycle(.4,.3,.3,5,0,5,.25)['normalized_productivity'],.8)
    def test_invalid_cycle(self):
        with self.assertRaises(ValueError):normalized_cycle(.4,.4,.4,5,0,0,.25)
    def test_seed_prefix(self):
        self.assertTrue(np.array_equal(np.random.default_rng(26007).random((100,5)),np.random.default_rng(26007).random((200,5))[:100]))
    def test_percentile(self): self.assertEqual(percentile([4,1,3,2],.5),2.5)
    def test_scenario_parser(self):
        d=json.loads((ROOT/'inputs/design.json').read_text());t=json.loads((ROOT/'scenarios/timelines.json').read_text());validate_design(d,t)
        bad=copy.deepcopy(t);bad['fog'][0]['available']='yes'
        with self.assertRaises(ValueError):validate_design(d,bad)
        bad=copy.deepcopy(t);bad['fog'][0]['range_m']=float('nan')
        with self.assertRaises(ValueError):validate_design(d,bad)
    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv';write_csv(p,[{'name':'comma,quoted','value':2}]);self.assertEqual(read_csv(p)[0]['name'],'comma,quoted')
    def test_corrupt_expected_result_rejected(self):
        with self.assertRaises(ValueError):close(1,1.01)
        # Actual verifier consumes a deliberately corrupt exported numeric row.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=read_csv(ROOT/'tables/sim01_safe_speed_vs_range.csv');data[0]['speed_mps']='999'
            write_csv(root/'tables/sim01_safe_speed_vs_range.csv',data)
            with self.assertRaisesRegex(ValueError,'numerical mismatch'):verify_numbers(root)
    def test_registry(self):
        data=read_csv(ROOT/'inputs/parameter_registry.csv')
        self.assertGreater(len(data),100)
        self.assertTrue(all(r['provenance_class'] and r['units'] and r['source'] for r in data))
    def test_master_unique(self):
        data=read_csv(ROOT/'results/SIH_SIMULATION_MASTER_RESULTS.csv');ids=[r['scenario_id'] for r in data]
        self.assertEqual(len(ids),len(set(ids)))
    def test_full_export_verification(self): self.assertEqual(verify_numbers(ROOT)['result'],'PASS')
    def test_failure_exit_code(self):
        import run_all
        with patch.object(run_all,'baseline_gate',side_effect=ValueError('deliberate test failure')), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_all.main(['--verify']),1)
    def test_hash_tamper_rejected(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'file.csv').write_text('expected')
            (root/'hashes.json').write_text(json.dumps({'file.csv':hashlib.sha256(b'expected').hexdigest()}))
            self.assertEqual(verify_hashes(root,root),1)
            (root/'file.csv').write_text('corrupted')
            with self.assertRaises(ValueError):verify_hashes(root,root)
    def test_artifact_manifest(self):
        # Existing manifest is checked on verification runs; initial generation has none.
        path=ROOT/'manifest.json'
        if path.exists():
            m=json.loads(path.read_text());self.assertEqual(m['traction'],'DISABLED_PHASE_1')
            self.assertFalse(m['hardware_access']);self.assertEqual(len(m['simulation_ids']),10)
