"""Resource ceilings for untrusted text extraction; called only in parser child."""
import os
_JOB=None

def limit_parser():
    global _JOB
    if os.name!='nt':
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
        resource.setrlimit(resource.RLIMIT_CPU,(8,8))
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
