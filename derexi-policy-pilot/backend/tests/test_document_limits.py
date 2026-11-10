"""Resource-boundary tests; native worker probes never connect to a database."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import document_limits as limits


@unittest.skipIf(os.name=='nt','POSIX limit selection; Windows uses Job Objects')
class LimitSelection(unittest.TestCase):
    def test_infinite_limits_use_requested_ceiling(self):
        import resource
        with patch.object(resource,'getrlimit',return_value=(resource.RLIM_INFINITY,)*2):
            self.assertEqual(limits._ceiling(resource,resource.RLIMIT_AS,256),256)

    def test_stricter_hard_limit_is_preserved(self):
        import resource
        with patch.object(resource,'getrlimit',return_value=(128,128)):
            self.assertEqual(limits._ceiling(resource,resource.RLIMIT_AS,256),128)

    def test_stricter_soft_limit_is_preserved(self):
        import resource
        with patch.object(resource,'getrlimit',return_value=(64,128)):
            self.assertEqual(limits._ceiling(resource,resource.RLIMIT_AS,256),64)

    def test_zero_limit_is_not_relaxed(self):
        import resource
        with patch.object(resource,'getrlimit',return_value=(0,128)):
            self.assertEqual(limits._ceiling(resource,resource.RLIMIT_AS,256),0)

    def test_linux_applies_bounded_memory_and_cpu(self):
        import resource
        with patch.object(limits.sys,'platform','linux'), patch.object(resource,'getrlimit',side_effect=[(64,128),(2,4)]), patch.object(resource,'setrlimit') as apply:
            limits.limit_parser()
            self.assertEqual(apply.call_args_list,[unittest.mock.call(resource.RLIMIT_CPU,(2,2)),unittest.mock.call(resource.RLIMIT_AS,(64,64))])

    def test_linux_memory_failure_fails_closed(self):
        import resource
        with patch.object(limits.sys,'platform','linux'), patch.object(resource,'getrlimit',return_value=(resource.RLIM_INFINITY,)*2), patch.object(resource,'setrlimit',side_effect=[None,OSError('unsupported')]):
            with self.assertRaises(OSError): limits.limit_parser()

    def test_mac_uses_supervision_and_stricter_data_limit(self):
        import resource
        with patch.object(limits.sys,'platform','darwin'), patch.object(resource,'getrlimit',side_effect=[(128,256),(2,4),(64,128)]), patch.object(resource,'setrlimit') as apply, patch.object(limits,'_supervise_mac') as supervise:
            limits.limit_parser()
            apply.assert_called_once_with(resource.RLIMIT_CPU,(2,2))
            supervise.assert_called_once_with(64)

    def test_unknown_platform_fails_closed(self):
        import resource
        with patch.object(limits.sys,'platform','unsupported'), patch.object(resource,'getrlimit',return_value=(resource.RLIM_INFINITY,)*2), patch.object(resource,'setrlimit'):
            with self.assertRaises(OSError): limits.limit_parser()

    def test_mac_probe_unavailable_prevents_fork(self):
        with patch.object(limits,'_mac_memory_reader',side_effect=OSError('unavailable')), patch.object(limits.os,'fork') as fork:
            with self.assertRaises(OSError): limits._supervise_mac(256)
            fork.assert_not_called()


@unittest.skipUnless(sys.platform=='darwin','Native macOS libproc/supervisor checks')
class MacWorker(unittest.TestCase):
    def worker(self,body):
        source=Path(limits.__file__).resolve()
        code="import runpy,sys,time; runpy.run_path(sys.argv[1])['limit_parser'](); "+body
        return subprocess.run([sys.executable,'-I','-c',code,str(source)],capture_output=True,timeout=12,env={})

    def test_native_memory_measurement(self):
        self.assertGreater(limits._mac_memory_reader()(os.getpid()),0)

    def test_valid_worker_completes(self):
        result=self.worker("print('completed')")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),b'completed')

    def test_allocation_over_memory_cap_is_stopped(self):
        result=self.worker("blocks=[]; exec('for _ in range(80):\\n blocks.append(bytearray(4*1024*1024)); time.sleep(0.02)'); print('unsafe completion')")
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn(b'unsafe completion',result.stdout)

    def test_wall_timeout_stops_sleeping_worker(self):
        result=self.worker("time.sleep(30); print('unsafe completion')")
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn(b'unsafe completion',result.stdout)

    def test_monitor_failure_stops_extraction(self):
        source=Path(limits.__file__).resolve()
        code="""import runpy,sys,time
scope=runpy.run_path(sys.argv[1])
def broken(pid): raise OSError('synthetic monitor failure')
scope['_supervise_mac'].__globals__['_mac_memory_reader']=lambda: broken
scope['_supervise_mac'](256*1024*1024)
time.sleep(1)
print('unsafe completion')
"""
        result=subprocess.run([sys.executable,'-I','-c',code,str(source)],capture_output=True,timeout=3,env={})
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn(b'unsafe completion',result.stdout)


if __name__=='__main__':
    unittest.main()
