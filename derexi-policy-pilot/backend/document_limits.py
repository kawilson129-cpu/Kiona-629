"""Resource ceilings for untrusted text extraction; called only in parser child."""
import os
import sys
_JOB=None

def _ceiling(resource, kind, requested):
    """Retain stricter inherited limits; never increase either limit."""
    soft,hard=resource.getrlimit(kind)
    return min([requested]+[v for v in (soft,hard) if v!=resource.RLIM_INFINITY])

def _mac_memory_reader():
    # Public libproc RUSAGE_INFO_V0 ABI, available since macOS 10.9.
    import ctypes as c
    class Usage(c.Structure):
        _fields_=[('uuid',c.c_ubyte*16)]+[(name,c.c_uint64) for name in
            ('user_time','system_time','idle_wakeups','interrupt_wakeups','pageins',
             'wired_size','resident_size','phys_footprint','start_time','exit_time')]
    lib=c.CDLL('/usr/lib/libproc.dylib',use_errno=True)
    lib.proc_pid_rusage.argtypes=[c.c_int,c.c_int,c.POINTER(Usage)]
    lib.proc_pid_rusage.restype=c.c_int
    def read(pid):
        usage=Usage()
        if lib.proc_pid_rusage(pid,0,c.byref(usage)):
            raise OSError(c.get_errno(),'Cannot measure parser memory')
        return max(usage.resident_size,usage.phys_footprint)
    read(os.getpid())  # Fail closed before permitting extraction.
    return read

def _supervise_mac(memory_limit):
    """Keep supervision outside the parser/GIL; child alone extracts documents."""
    import signal
    import time
    read=_mac_memory_reader()
    pid=os.fork()
    if pid==0:
        return
    # The supervisor exits before the API's unchanged 12-second timeout.
    deadline=time.monotonic()+10
    try:
        while True:
            done,status=os.waitpid(pid,os.WNOHANG)
            if done:
                os._exit(os.waitstatus_to_exitcode(status) if os.WIFEXITED(status) else 1)
            if time.monotonic()>=deadline or read(pid)>memory_limit:
                break
            time.sleep(0.01)
    except BaseException:
        # A missing/failed memory probe must never leave extraction unprotected.
        # Exit can race the probe; preserve an already completed worker's status.
        done,status=os.waitpid(pid,os.WNOHANG)
        if done:
            os._exit(os.waitstatus_to_exitcode(status) if os.WIFEXITED(status) else 1)
    try:
        os.kill(pid,signal.SIGKILL)
    except ProcessLookupError:
        pass
    os.waitpid(pid,0)
    os._exit(1)

def limit_parser():
    global _JOB
    if os.name!='nt':
        import resource
        memory=_ceiling(resource,resource.RLIMIT_AS,256*1024*1024)
        cpu=_ceiling(resource,resource.RLIMIT_CPU,8)
        resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
        if sys.platform=='darwin':
            # Darwin aliases AS to RSS; setrlimit is not a usable allocation cap.
            # Respect any stricter inherited data ceiling as well.
            memory=min(memory,_ceiling(resource,resource.RLIMIT_DATA,memory))
            _supervise_mac(memory)
        elif sys.platform.startswith('linux'):
            resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        else:
            raise OSError('Unsupported parser memory protection')
        return
    import ctypes as c
    from ctypes import wintypes as w
    class Basic(c.Structure):
        _fields_=[('process_time',c.c_longlong),('job_time',c.c_longlong),('flags',w.DWORD),
            ('min_ws',c.c_size_t),('max_ws',c.c_size_t),('active',w.DWORD),
            ('affinity',c.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
    class IO(c.Structure):
        _fields_=[(name,c.c_ulonglong) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
    class Extended(c.Structure):
        _fields_=[('basic',Basic),('io',IO),('process_memory',c.c_size_t),('job_memory',c.c_size_t),
            ('peak_process',c.c_size_t),('peak_job',c.c_size_t)]
    kernel=c.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[c.c_void_p,w.LPCWSTR];kernel.CreateJobObjectW.restype=w.HANDLE
    kernel.SetInformationJobObject.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD]
    kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
    kernel.GetCurrentProcess.restype=w.HANDLE
    _JOB=kernel.CreateJobObjectW(None,None)
    info=Extended();info.basic.flags=0x100|0x2;info.basic.process_time=8*10_000_000
    info.process_memory=256*1024*1024
    if not _JOB or not kernel.SetInformationJobObject(_JOB,9,c.byref(info),c.sizeof(info)) or not kernel.AssignProcessToJobObject(_JOB,kernel.GetCurrentProcess()):
        raise OSError('Cannot establish parser resource limits')
