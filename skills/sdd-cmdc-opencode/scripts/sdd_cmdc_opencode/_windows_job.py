from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from typing import Any


JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000


class JobError(RuntimeError):
    def __init__(
        self, operation: str, message: str | None = None, error_code: int | None = None
    ) -> None:
        self.operation = operation
        self.error_code = (
            ctypes.get_last_error() if error_code is None else error_code
        )
        detail = message or f"Win32 error {self.error_code}"
        super().__init__(f"{operation} failed ({self.error_code}): {detail}")


class _JobObjectBasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class _JobObjectExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _JobObjectBasicLimitInformation),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _JobObjectBasicAccountingInformation(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


_KERNEL32: Any | None = None


def _kernel32() -> Any:
    global _KERNEL32
    if os.name != "nt":
        raise JobError("Windows Job Objects", "unsupported platform")
    if _KERNEL32 is None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle_type = wintypes.HANDLE
        kernel32.CreateJobObjectW.argtypes = [handle_type, wintypes.LPCWSTR]
        kernel32.CreateJobObjectW.restype = handle_type
        kernel32.SetInformationJobObject.argtypes = [
            handle_type, wintypes.INT, wintypes.LPVOID, wintypes.DWORD
        ]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = [handle_type, handle_type]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.TerminateJobObject.argtypes = [handle_type, wintypes.UINT]
        kernel32.TerminateJobObject.restype = wintypes.BOOL
        kernel32.QueryInformationJobObject.argtypes = [
            handle_type,
            wintypes.INT,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        kernel32.QueryInformationJobObject.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [handle_type]
        kernel32.CloseHandle.restype = wintypes.BOOL
        _KERNEL32 = kernel32
    return _KERNEL32


class Job:
    """Private Job Object wrapper whose handle closes only after empty proof."""

    def __init__(self, handle: wintypes.HANDLE) -> None:
        self._handle = handle
        self._closed = False
        self._empty_verified = False

    @classmethod
    def create(cls) -> Job:
        kernel32 = _kernel32()
        handle = kernel32.CreateJobObjectW(None, None)
        if not handle:
            raise JobError("CreateJobObjectW")
        job = cls(handle)
        try:
            limits = _JobObjectExtendedLimitInformation()
            limits.BasicLimitInformation.LimitFlags = (
                JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            )
            if not kernel32.SetInformationJobObject(
                handle,
                JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                ctypes.byref(limits),
                ctypes.sizeof(limits),
            ):
                raise JobError("SetInformationJobObject")
        except BaseException:
            try:
                kernel32.CloseHandle(handle)
            except BaseException:
                pass
            raise
        return job

    @property
    def closed(self) -> bool:
        return self._closed

    def assign_process(self, process: Any) -> None:
        if self._closed:
            raise JobError("AssignProcessToJobObject", "job is closed")
        raw_handle = getattr(process, "_handle", None)
        if raw_handle is None:
            raise JobError(
                "AssignProcessToJobObject", "process handle is unavailable"
            )
        try:
            process_handle = wintypes.HANDLE(int(raw_handle))
        except (TypeError, ValueError) as exc:
            raise JobError(
                "AssignProcessToJobObject", "invalid process handle"
            ) from exc
        if not _kernel32().AssignProcessToJobObject(
            self._handle, process_handle
        ):
            raise JobError("AssignProcessToJobObject")

    def active_processes(self) -> int:
        if self._closed:
            raise JobError("QueryInformationJobObject", "job is closed")
        info = _JobObjectBasicAccountingInformation()
        returned = wintypes.DWORD()
        if not _kernel32().QueryInformationJobObject(
            self._handle,
            JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info),
            ctypes.byref(returned),
        ):
            raise JobError("QueryInformationJobObject")
        active = int(info.ActiveProcesses)
        if active == 0:
            self._empty_verified = True
        return active

    def terminate(self, exit_code: int = 1) -> None:
        if self._closed:
            raise JobError("TerminateJobObject", "job is closed")
        if not _kernel32().TerminateJobObject(self._handle, exit_code):
            raise JobError("TerminateJobObject")

    def close(self) -> None:
        if self._closed:
            return
        if not self._empty_verified:
            raise JobError(
                "CloseHandle",
                "refusing to close Job Object before empty-process proof",
            )
        if not _kernel32().CloseHandle(self._handle):
            raise JobError("CloseHandle")
        self._closed = True

    def __enter__(self) -> Job:
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        if self._empty_verified and not self._closed:
            self.close()
