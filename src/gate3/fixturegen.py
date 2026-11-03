"""Pure stdlib deterministic ISO-BMFF synthetic fixture generator.

FR-02 requires fixture recipes that express composition offsets (``ctts``), duplicate
presentation PTS, multiple ``trak`` boxes (video/audio, ambiguous multi-video) and the
deterministic/unsupported ``elst`` edit-list forms.  ``generate_fixture``'s return shape is
unchanged (no timing oracle key); the recipes below add container shapes only.
"""
from __future__ import annotations
import contextlib,hashlib,os,pathlib,struct,tempfile
@contextlib.contextmanager
def scratch_dir(name="gate3"):
    root=os.environ.get("GATE3_ARTIFACT_ROOT")
    if root:
        d=pathlib.Path(root)/name;d.mkdir(parents=True,exist_ok=True);yield str(d)
    else:
        with tempfile.TemporaryDirectory() as d:yield d
def _box(k,p):return struct.pack(">I",8+len(p))+k+p
def _full(k,v,f,p):return _box(k,struct.pack(">B",v)+f.to_bytes(3,"big")+p)
def _ftyp():return _box(b"ftyp",b"isom"+struct.pack(">I",0x200)+b"isomiso2mp41")
def _mvhd(ts,d):return _full(b"mvhd",0,0,struct.pack(">IIII",0,0,ts,d)+b"\0"*80)
def _tkhd(track,d):return _full(b"tkhd",0,3,struct.pack(">IIIII",0,0,track,0,d)+b"\0"*60)
def _elst(mt):return _full(b"elst",0,0,struct.pack(">I",1)+struct.pack(">IiHH",0,mt,1,0))
def _elst_entries(media_times):
    p=struct.pack(">I",len(media_times))
    for mt in media_times:p+=struct.pack(">IiHH",0,mt,1,0)
    return _full(b"elst",0,0,p)
def _mdhd(ts,d):return _full(b"mdhd",0,0,struct.pack(">IIIIHH",0,0,ts,d,0x55C4,0))
def _hdlr(handler=b"vide"):return _full(b"hdlr",0,0,b"\0"*4+handler+b"\0"*12+b"Synthetic\0")
def _stsd():
    e=struct.pack(">I",16)+b"synt"+b"\0"*6+struct.pack(">H",1);return _full(b"stsd",0,0,struct.pack(">I",1)+e)
def _stts(ds):
    runs=[]
    for d in ds:
        if runs and runs[-1][1]==d:runs[-1][0]+=1
        else:runs.append([1,d])
    p=struct.pack(">I",len(runs))+b"".join(struct.pack(">II",c,d) for c,d in runs)
    return _full(b"stts",0,0,p)
def _ctts(offsets):
    """Synthetic composition-offset table: entry_count then one signed offset per sample.

    ``pts(i) = dts(i) + offset(i)``; a signed negative offset is the B-frame reorder case.
    """
    p=struct.pack(">I",len(offsets))+b"".join(struct.pack(">i",int(o)) for o in offsets)
    return _full(b"ctts",1,0,p)
def _tables(n):
    return (_full(b"stsc",0,0,struct.pack(">I",1)+struct.pack(">III",1,n,1))+
            _full(b"stsz",0,0,struct.pack(">II",0,n))+
            _full(b"stco",0,0,struct.pack(">I",1)+struct.pack(">I",0)))
def sample_deltas_from_pts(pts,tail):
    if not pts or tail<=0:raise ValueError("invalid timing")
    ds=[b-a for a,b in zip(pts,pts[1:])]
    if any(x<=0 for x in ds):raise ValueError("PTS must increase")
    return tuple(ds+[tail])
def _trak_bytes(*,media_timescale,sample_deltas,track=1,track_id=None,handler=b"vide",media_time_offset=0,
                edit_media_times=None,ctts_offsets=None,declared_duration=None):
    duration=sum(sample_deltas);declared=duration if declared_duration is None else declared_duration
    children=_stsd()+_stts(sample_deltas)
    if ctts_offsets is not None:children+=_ctts(ctts_offsets)
    children+=_tables(len(sample_deltas))
    stbl=_box(b"stbl",children)
    mdia=_box(b"mdia",_mdhd(media_timescale,declared)+_hdlr(handler)+_box(b"minf",stbl))
    if edit_media_times is not None:edts=_box(b"edts",_elst_entries(list(edit_media_times)))
    elif media_time_offset:edts=_box(b"edts",_elst(media_time_offset))
    else:edts=b""
    return _box(b"trak",_tkhd(track if track_id is None else track_id,declared)+edts+mdia)
def build_mp4(*,media_timescale,sample_deltas,media_time_offset=0,variant_tag=b"",declared_duration=None,
              ctts_offsets=None,handler=b"vide",edit_media_times=None):
    trak=_trak_bytes(media_timescale=media_timescale,sample_deltas=sample_deltas,handler=handler,
                     media_time_offset=media_time_offset,edit_media_times=edit_media_times,
                     ctts_offsets=ctts_offsets,declared_duration=declared_duration)
    duration=sum(sample_deltas)
    return _ftyp()+_box(b"moov",_mvhd(media_timescale,duration)+trak)+(_box(b"free",variant_tag) if variant_tag else b"")+_box(b"mdat",b"\0"*8)
def build_multi_trak_mp4(*,media_timescale,traks):
    """``traks`` is a sequence of keyword mappings accepted by ``_trak_bytes`` (minus track id)."""
    duration=sum(sum(t["sample_deltas"]) for t in traks)
    boxes=b"".join(_trak_bytes(track=i+1,**t) for i,t in enumerate(traks))
    return _ftyp()+_box(b"moov",_mvhd(media_timescale,duration)+boxes)+_box(b"mdat",b"\0"*8)
def _single_track_blob():
    return build_mp4(media_timescale=1000,sample_deltas=(40,40))
def _replace_tkhd(blob, replacement):
    at=blob.index(b"tkhd")-4
    size=struct.unpack_from(">I",blob,at)[0]
    delta=len(replacement)-size
    result=bytearray(blob[:at]+replacement+blob[at+size:])
    for kind in (b"trak",b"moov"):
        parent=result.index(kind)-4
        parent_size=struct.unpack_from(">I",result,parent)[0]
        struct.pack_into(">I",result,parent,parent_size+delta)
    return bytes(result)
def build_no_tkhd_mp4():
    return _replace_tkhd(_single_track_blob(),b"")
def build_short_tkhd_mp4():
    return _replace_tkhd(_single_track_blob(),struct.pack(">I4s",80,b"tkhd")+b"\0"*72)
def build_zero_size_tkhd_mp4():
    blob=_single_track_blob();at=blob.index(b"tkhd")-4
    return blob[:at]+b"\0\0\0\0"+blob[at+4:]
def build_large_size_tkhd_mp4():
    blob=_single_track_blob();at=blob.index(b"tkhd")-4
    size=struct.unpack_from(">I",blob,at)[0];payload=blob[at+8:at+size]
    replacement=struct.pack(">I4sQ",1,b"tkhd",16+len(payload))+payload
    return _replace_tkhd(blob,replacement)
def build_tkhd_version_2_mp4():
    blob=_single_track_blob();at=blob.index(b"tkhd")+4
    return blob[:at]+b"\x02"+blob[at+1:]
def build_duplicate_track_id_mp4():
    traks=[dict(media_timescale=1000,sample_deltas=(40,),track_id=1),dict(media_timescale=48000,sample_deltas=(1024,),track_id=1,handler=b"soun")]
    return build_multi_trak_mp4(media_timescale=1000,traks=traks)
def build_reversed_track_ids_mp4():
    traks=[dict(media_timescale=1000,sample_deltas=(40,),track_id=2,handler=b"vide"),dict(media_timescale=48000,sample_deltas=(1024,),track_id=1,handler=b"soun")]
    return build_multi_trak_mp4(media_timescale=1000,traks=traks)
def build_timingless_trak_mp4():
    mdia=_box(b"mdia",_mdhd(1000,80)+_hdlr(b"vide")+_box(b"minf",_box(b"stbl",_stsd()+_tables(2))))
    trak=_box(b"trak",_tkhd(1,80)+mdia)
    return _ftyp()+_box(b"moov",_mvhd(1000,80)+trak)+_box(b"mdat",b"\0"*8)

RECIPES={
 "cfr_4s_shape":{"media_timescale":25,"pts_ticks":(0,13,25,38,50,63,75,88),"tail_duration_ticks":12,"check_in_method":"recipe + oracle metadata only"},
 "cfr_30000_1001":{"media_timescale":30000,"pts_ticks":(0,1001,2002),"tail_duration_ticks":1001,"check_in_method":"recipe + oracle metadata only"},
 "vfr_nonuniform":{"media_timescale":1000,"pts_ticks":(0,40,80,160,280),"tail_duration_ticks":500,"check_in_method":"recipe + oracle metadata only"},
 "revision_reencode":{"media_timescale":25,"pts_ticks":(0,13,25,38,50,63,75,88),"tail_duration_ticks":12,"variant_tag":b"reencode-v2","check_in_method":"recipe + oracle metadata only"},
 "origin_nonzero":{"media_timescale":25,"pts_ticks":(0,13,25,38,50,63,75,88),"tail_duration_ticks":12,"media_time_offset":125,"check_in_method":"recipe + oracle metadata only"},
 # FR-02 composition/reorder/duplicate/multi-track/edit-list shapes.
 "ctts_reorder_signed":{"media_timescale":1000,"sample_deltas":(40,40,40,40),"ctts_offsets":(0,80,-40,-40),"check_in_method":"recipe + oracle metadata only","expected_properties":["signed-composition-offsets","pts-differs-from-dts"]},
 "duplicate_pts_retained":{"media_timescale":1000,"sample_deltas":(5,0,5,5),"check_in_method":"recipe + oracle metadata only","expected_properties":["duplicate-presentation-pts-retained"]},
 "multitrack_video_ambiguous":{"media_timescale":1000,"traks":[{"media_timescale":1000,"sample_deltas":(40,40,40),"handler":b"vide"},{"media_timescale":48000,"sample_deltas":(1001,1001,1001),"handler":b"vide"}],"check_in_method":"recipe + oracle metadata only","expected_properties":["ambiguous-multiple-video-timing-traks"]},
 "audio_then_video":{"media_timescale":1000,"traks":[{"media_timescale":1000,"sample_deltas":(40,40,40),"handler":b"soun"},{"media_timescale":1000,"sample_deltas":(50,50,50),"handler":b"vide"}],"check_in_method":"recipe + oracle metadata only","expected_properties":["non-video-timing-trak-before-video-trak"]},
 "elst_empty":{"media_timescale":25,"pts_ticks":(0,13,25,38,50,63,75,88),"tail_duration_ticks":12,"edit_media_times":(),"check_in_method":"recipe + oracle metadata only","expected_properties":["unsupported-empty-edit-list"]},
 "elst_multi_segment":{"media_timescale":25,"pts_ticks":(0,13,25,38,50,63,75,88),"tail_duration_ticks":12,"edit_media_times":(125,250),"check_in_method":"recipe + oracle metadata only","expected_properties":["unsupported-multi-segment-edit-list"]},
 "elst_negative_origin":{"media_timescale":25,"pts_ticks":(0,13,25,38,50,63,75,88),"tail_duration_ticks":12,"edit_media_times":(-1,),"check_in_method":"recipe + oracle metadata only","expected_properties":["unsupported-negative-edit-list-origin"]},
 "no_tkhd":{"builder":"build_no_tkhd_mp4","media_timescale":1000,"sample_deltas":(40,40),"check_in_method":"recipe + oracle metadata only"},
 "short_tkhd":{"builder":"build_short_tkhd_mp4","media_timescale":1000,"sample_deltas":(40,40),"check_in_method":"recipe + oracle metadata only"},
 "zero_size_tkhd":{"builder":"build_zero_size_tkhd_mp4","media_timescale":1000,"sample_deltas":(40,40),"check_in_method":"recipe + oracle metadata only"},
 "large_size_tkhd":{"builder":"build_large_size_tkhd_mp4","media_timescale":1000,"sample_deltas":(40,40),"check_in_method":"recipe + oracle metadata only"},
 "tkhd_version_2":{"builder":"build_tkhd_version_2_mp4","media_timescale":1000,"sample_deltas":(40,40),"check_in_method":"recipe + oracle metadata only"},
 "duplicate_track_id":{"builder":"build_duplicate_track_id_mp4","media_timescale":1000,"sample_deltas":(40,),"check_in_method":"recipe + oracle metadata only"},
 "reversed_track_ids":{"builder":"build_reversed_track_ids_mp4","media_timescale":1000,"sample_deltas":(40,),"check_in_method":"recipe + oracle metadata only"},
 "timingless_trak":{"builder":"build_timingless_trak_mp4","media_timescale":1000,"sample_deltas":(),"declared_duration":80,"timingless":True,"check_in_method":"recipe + oracle metadata only"},
}
def _traks_for_recipe(recipe):
    if "traks" in recipe:
        return [dict(t) for t in recipe["traks"]]
    if "sample_deltas" in recipe:
        deltas=tuple(recipe["sample_deltas"])
    else:
        deltas=sample_deltas_from_pts(tuple(recipe["pts_ticks"]),recipe["tail_duration_ticks"])
    return [{"media_timescale":recipe["media_timescale"],"sample_deltas":deltas,
             "handler":recipe.get("handler",b"vide"),"media_time_offset":recipe.get("media_time_offset",0),
             "edit_media_times":recipe.get("edit_media_times"),"ctts_offsets":recipe.get("ctts_offsets")}]
def build_recipe(recipe_name):
    r=RECIPES[recipe_name]
    if "builder" in r:return globals()[r["builder"]]()
    traks=_traks_for_recipe(r)
    if len(traks)==1:
        t=traks[0];deltas=t["sample_deltas"]
        return build_mp4(media_timescale=t["media_timescale"],sample_deltas=deltas,
                         media_time_offset=t.get("media_time_offset",0),variant_tag=r.get("variant_tag",b""),
                         ctts_offsets=t.get("ctts_offsets"),handler=t.get("handler",b"vide"),
                         edit_media_times=t.get("edit_media_times"))
    return build_multi_trak_mp4(media_timescale=r["media_timescale"],traks=traks)
def generate_fixture(recipe_name,out_dir,*,out_name):
    r=RECIPES[recipe_name];blob=build_recipe(recipe_name)
    first=_traks_for_recipe(r)[0];ds=tuple(first["sample_deltas"])
    p=pathlib.Path(out_dir)/out_name;p.write_bytes(blob)
    mdhd_duration=r.get("declared_duration",sum(ds))
    timing_bytes=_mdhd(first["media_timescale"],mdhd_duration)
    if not r.get("timingless"):
        timing_bytes=_stts(ds)+timing_bytes
    return {"fixture":recipe_name,"path":str(p),"sha256":hashlib.sha256(blob).hexdigest(),"container_sha256_of_stts":hashlib.sha256(timing_bytes).hexdigest(),"byte_count":len(blob)}
