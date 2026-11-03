from __future__ import annotations
import json,os,pathlib,tempfile,time
WALL_CLOCK_CEILING_SECONDS=300;DISK_CEILING_MIB=256;MAX_CONCURRENCY=1
# FR-09: a lock whose owner identity cannot be read may be recovered once it has outlived the
# bounded ceiling. A provably dead owner recovers immediately; a provably live owner never does.
STALE_LOCK_AGE_SECONDS=WALL_CLOCK_CEILING_SECONDS
def _lock_path():return pathlib.Path(tempfile.gettempdir())/"gate3-heavy-lease.lock"
def _is_number(value):return isinstance(value,(int,float)) and not isinstance(value,bool)
def directory_mib(path):
    total=0
    for r,_d,fs in os.walk(path):
        for f in fs:
            try:total+=os.path.getsize(os.path.join(r,f))
            except OSError:pass
    return total/(1024*1024)
def _read_lock_record(path):
    try:return json.loads(pathlib.Path(path).read_text())
    except Exception:return None
def _pid_is_provably_alive(pid):
    try:os.kill(pid,0)
    except ProcessLookupError:return False
    except OSError:return True
    return True
def _lock_owner_liveness(record):
    """True/False for a readable integer owner pid; None when identity cannot be read."""
    if not isinstance(record,dict):return None
    pid=record.get("owner_pid")
    if not isinstance(pid,int) or isinstance(pid,bool):return None
    return _pid_is_provably_alive(pid)
def _lock_is_stale(path):
    """Provable abandonment only: a released owner, a provably dead owner, or an unreadable lock
    older than the bounded ceiling. A provably live owner is never stale (concurrency = 1)."""
    p=pathlib.Path(path);record=_read_lock_record(p)
    if isinstance(record,dict):
        if record.get("released_at") is not None:return True
        alive=_lock_owner_liveness(record)
        if alive is not None:return not alive
        acquired=record.get("acquired_at")
        if _is_number(acquired):return (time.time()-acquired)>STALE_LOCK_AGE_SECONDS
        return False
    try:age=time.time()-p.stat().st_mtime
    except OSError:return False
    return age>STALE_LOCK_AGE_SECONDS
def _describe_lock_owner(path):
    record=_read_lock_record(path)
    if isinstance(record,dict) and record.get("attempt_id"):
        return "owner_pid=%r attempt_id=%r"%(record.get("owner_pid"),record.get("attempt_id"))
    return "unreadable lock record"
def resource_consistency_errors(record):
    """FR-09: recompute resource consistency from the observed fields against the policy ceilings.

    Ceiling violations are reported first (each names the ceiling it breached); structural
    contradictions follow. An unobserved field is NOT_OBSERVED and is skipped, never treated as a
    violation, so a record produced by an older lease stays admissible.
    """
    if not isinstance(record,dict):return ["RESOURCE_EVIDENCE_NOT_OBJECT"]
    errors=[];violated=False
    wall=record.get("observed_wall_clock_seconds")
    if _is_number(wall) and wall>WALL_CLOCK_CEILING_SECONDS:errors.append("RESOURCE_CEILING_WALL_CLOCK_EXCEEDED");violated=True
    disk=record.get("observed_peak_disk_mib")
    if _is_number(disk) and disk>DISK_CEILING_MIB:errors.append("RESOURCE_CEILING_DISK_EXCEEDED");violated=True
    children=record.get("observed_max_heavy_children")
    if _is_number(children) and children>MAX_CONCURRENCY:errors.append("RESOURCE_CEILING_CONCURRENCY_EXCEEDED");violated=True
    configured=record.get("configured_concurrency")
    if _is_number(configured) and configured>MAX_CONCURRENCY:errors.append("RESOURCE_CEILING_CONCURRENCY_EXCEEDED");violated=True
    declared=record.get("ceilings");declared_contradiction=False
    if isinstance(declared,dict):
        for key,authority in (("wall_clock_seconds",WALL_CLOCK_CEILING_SECONDS),("disk_mib",DISK_CEILING_MIB),("concurrency",MAX_CONCURRENCY)):
            if key in declared and (not _is_number(declared[key]) or declared[key]>authority):declared_contradiction=True
    elif declared is not None:declared_contradiction=True
    if declared_contradiction:errors.append("RESOURCE_EVIDENCE_INCONSISTENT_CEILINGS");violated=True
    for key in ("observed_wall_clock_seconds","observed_peak_disk_mib","observed_max_heavy_children","configured_concurrency"):
        value=record.get(key)
        if value is not None and not _is_number(value):errors.append("RESOURCE_EVIDENCE_INCONSISTENT_"+key.upper());violated=True
    if record.get("resource_failure") is None and violated:
        errors.append("RESOURCE_EVIDENCE_INCONSISTENT_FAILURE_VERDICT")
    return errors
class Lease:
    def __init__(self,*,evidence_dir,watched_dir=None,attempt_id=None,run_id=None):
        self.evidence_dir=pathlib.Path(evidence_dir);self.watched_dir=watched_dir or evidence_dir
        self.run_id=run_id
        self.attempt_id=attempt_id if attempt_id is not None else "attempt-%d-%d"%(os.getpid(),time.time_ns())
        self.lock_path=_lock_path()
        self._acquired_at=None;self._released_at=None;self._peak_disk_mib=0.;self._resource_failure=None
        self._live=0;self._max=0;self._phases=[];self._phase_windows=[];self._phase_open={}
        self._recovered=False;self._acquisition_record=None
    def _lock_payload(self):
        return json.dumps({"owner_pid":os.getpid(),"attempt_id":self.attempt_id,"run_id":self.run_id,"acquired_at":time.time()},sort_keys=True).encode()
    def _write_lock_exclusive(self,payload):
        """Create the lock with its full JSON identity already written; False if it exists."""
        lock=self.lock_path;lock.parent.mkdir(parents=True,exist_ok=True)
        tmp=lock.with_name("%s.tmp.%d.%d"%(lock.name,os.getpid(),time.time_ns()))
        fd=os.open(str(tmp),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
        try:os.write(fd,payload);os.fsync(fd)
        finally:os.close(fd)
        try:
            os.link(str(tmp),str(lock));return True
        except FileExistsError:return False
        except OSError:
            try:fd=os.open(str(lock),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
            except FileExistsError:return False
            with os.fdopen(fd,"wb") as handle:handle.write(payload);handle.flush();os.fsync(handle.fileno())
            return True
        finally:
            try:tmp.unlink()
            except OSError:pass
    def _recover_stale_lock(self):
        """Atomically claim the stale inode so at most one recoverer can move it away."""
        quarantine=self.lock_path.with_name("%s.stale.%d.%d"%(self.lock_path.name,os.getpid(),time.time_ns()))
        try:os.rename(str(self.lock_path),str(quarantine))
        except OSError:return False
        try:quarantine.unlink()
        except OSError:pass
        return True
    def __enter__(self):
        payload=self._lock_payload()
        if not self._write_lock_exclusive(payload):
            if not _lock_is_stale(self.lock_path):
                raise RuntimeError("lease held: "+_describe_lock_owner(self.lock_path))
            if not self._recover_stale_lock() or not self._write_lock_exclusive(payload):
                raise RuntimeError("lease held: stale-lock recovery lost the race")
            self._recovered=True
        self._acquisition_record=payload;self._phases=[];self._phase_windows=[];self._phase_open={}
        self._acquired_at=time.monotonic();return self
    def __exit__(self,*_):
        self._released_at=time.monotonic()
        if self._recovered:self._persist_released_record()
        else:self._remove_owned_lock()
    def _remove_owned_lock(self):
        record=_read_lock_record(self.lock_path)
        if isinstance(record,dict) and record.get("owner_pid")==os.getpid() and record.get("attempt_id")==self.attempt_id:
            try:self.lock_path.unlink()
            except OSError:pass
    def _persist_released_record(self):
        """A takeover keeps its ownership record after release: R-09-12 requires the recovered lock
        to name the new owner after the lease exits, because the takeover is the auditable event."""
        record=_read_lock_record(self.lock_path)
        if not (isinstance(record,dict) and record.get("owner_pid")==os.getpid() and record.get("attempt_id")==self.attempt_id):
            try:record=json.loads(self._acquisition_record.decode()) if self._acquisition_record else {}
            except Exception:record={}
        record.update({"released_at":time.time(),"suite_completed":True})
        tmp=self.lock_path.with_name("%s.rel.%d.%d"%(self.lock_path.name,os.getpid(),time.time_ns()))
        try:
            tmp.write_bytes(json.dumps(record,sort_keys=True).encode());os.replace(str(tmp),str(self.lock_path))
        except OSError:
            try:tmp.unlink()
            except OSError:pass
    def sample_disk(self):self._peak_disk_mib=max(self._peak_disk_mib,directory_mib(self.watched_dir))
    def heavy_child_enter(self):self._live+=1;self._max=max(self._max,self._live);return self
    def heavy_child_exit(self):self._live=max(0,self._live-1)
    def phase_enter(self,name):
        label=str(name)
        if label not in self._phases:self._phases.append(label)
        self._phase_open[label]=time.monotonic();return self
    def phase_exit(self,name):
        label=str(name);started=self._phase_open.pop(label,None)
        self._phase_windows.append({"name":label,"seconds":None if started is None else time.monotonic()-started,"completed":started is not None})
        if label not in self._phases:self._phases.append(label)
        return self
    @property
    def elapsed_seconds(self):return 0 if self._acquired_at is None else (self._released_at or time.monotonic())-self._acquired_at
    @property
    def observed_wall_clock_seconds(self):
        if self._acquired_at is None or self._released_at is None:
            raise RuntimeError("whole-suite wall clock is not complete while the lease is held")
        return self._released_at-self._acquired_at
    def mark_resource_failure(self,r):self._resource_failure=r
    def evidence(self):
        completed=self._released_at is not None
        wall=(self._released_at-self._acquired_at) if (completed and self._acquired_at is not None) else None
        failure=self._resource_failure
        if failure is None:
            if wall is not None and wall>WALL_CLOCK_CEILING_SECONDS:failure="WALL_CLOCK_EXCEEDED"
            elif self._peak_disk_mib>DISK_CEILING_MIB:failure="DISK_EXCEEDED"
            elif self._max>MAX_CONCURRENCY:failure="CONCURRENCY_EXCEEDED"
        ev={"observed_wall_clock_seconds":wall,"observed_peak_disk_mib":self._peak_disk_mib,"observed_max_heavy_children":self._max or None,"configured_concurrency":MAX_CONCURRENCY,"ceilings":{"wall_clock_seconds":WALL_CLOCK_CEILING_SECONDS,"disk_mib":DISK_CEILING_MIB,"concurrency":MAX_CONCURRENCY},"resource_failure":failure,"owner_pid":os.getpid(),"attempt_id":self.attempt_id,"run_id":self.run_id,"lock_path":str(self.lock_path),"suite_completed":completed,"phases":list(self._phases),"phase_windows":[dict(w) for w in self._phase_windows]}
        self.evidence_dir.mkdir(parents=True,exist_ok=True);(self.evidence_dir/"lease-evidence.json").write_text(json.dumps(ev,indent=2,sort_keys=True));return ev
