from dataclasses import dataclass
from gate3.rational import TimeBase
@dataclass(frozen=True)
class TimelineDomain:
    domain_id:str
    time_base:TimeBase
    domain_name:str="timeline_time"
    def tick_to_seconds(self,ticks):return self.time_base.ticks_to_seconds(ticks)
@dataclass(frozen=True)
class TimelineInterval:
    placement_id:str;start_ticks:int;end_ticks:int;domain:TimelineDomain;endpoint_semantics:str="half_open"
    def __post_init__(self):
        if self.endpoint_semantics!="half_open" or self.end_ticks<=self.start_ticks:raise ValueError("invalid timeline interval")
    @property
    def duration_ticks(self):return self.end_ticks-self.start_ticks
