from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DistributionType(str, Enum):
    """Supported probability distributions"""
    CONSTANT = "constant"
    EXPONENTIAL = "exponential"
    NORMAL = "normal"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"

class ProcessingTime(BaseModel):
    """Processing time specification"""
    distribution: DistributionType
    params: dict[str, float]  # e.g., {"mean": 5.0, "std": 1.0} for normal

    @field_validator('params')
    @classmethod
    def validate_params(cls, v, info):
        dist = info.data.get('distribution')
        required = {
            DistributionType.CONSTANT: ['value'],
            DistributionType.EXPONENTIAL: ['mean'],
            DistributionType.NORMAL: ['mean', 'std'],
            DistributionType.UNIFORM: ['low', 'high'],
            DistributionType.TRIANGULAR: ['low', 'mode', 'high']
        }
        if set(v.keys()) != set(required[dist]):
            raise ValueError(f"{dist} requires params: {required[dist]}")
        return v

class WorkStation(BaseModel):
    """Discrete event simulation workstation"""
    id: str = Field(..., description="Unique workstation identifier")
    name: Optional[str] = None

    # Processing
    processing_time: ProcessingTime
    capacity: int = Field(1, ge=1, description="Number of parallel resources")

    # Routing
    predecessors: list[str] = Field(default_factory=list)
    successors: list[str] = Field(default_factory=list)

    # Reliability
    mtbf: Optional[float] = Field(None, ge=0, description="Mean time between failures")
    mttr: Optional[float] = Field(None, ge=0, description="Mean time to repair")
    failure_distribution: DistributionType = DistributionType.EXPONENTIAL
    repair_distribution: DistributionType = DistributionType.EXPONENTIAL

    # Buffer
    input_buffer_capacity: Optional[int] = Field(None, ge=0)
    output_buffer_capacity: Optional[int] = Field(None, ge=0)

    # Stats tracking
    track_utilization: bool = True
    track_queue_length: bool = True

class RoutingLogic(str, Enum):
    """Job routing strategies"""
    SEQUENCE = "sequence"  # Follow predefined sequence
    SHORTEST_QUEUE = "shortest_queue"  # Pick station with smallest queue
    RANDOM = "random"  # Random selection from successors
    PRIORITY = "priority"  # Based on job priority

class JobType(BaseModel):
    """Defines a type of job/part flowing through the system"""

    id: str = Field(..., description="Unique job type identifier")
    name: Optional[str] = None

    # Routing
    routing_logic: RoutingLogic = RoutingLogic.SEQUENCE
    route: list[str] = Field(..., description="Ordered list of workstation IDs")

    # Processing times per station (overrides station defaults if specified)
    station_processing_times: dict[str, ProcessingTime] = Field(
        default_factory=dict,
        description="Station-specific processing times for this job type",
    )

    # Priority and attributes
    priority: int = Field(0, description="Higher values = higher priority")
    due_date_offset: Optional[float] = Field(
        None, ge=0, description="Time from creation to due date"
    )

    # Rework/scrap
    scrap_probability: dict[str, float] = Field(
        default_factory=dict, description="Station ID -> scrap probability (0-1)"
    )
    rework_probability: dict[str, float] = Field(
        default_factory=dict, description="Station ID -> rework probability (0-1)"
    )
    rework_station: Optional[str] = Field(
        None, description="Station to send rework jobs to"
    )

    # Arrival pattern
    interarrival_time: Optional[ProcessingTime] = Field(
        None, description="Time between job arrivals (if this is a primary job type)"
    )

    # Batching
    batch_size: int = Field(1, ge=1, description="Jobs per batch")
    lot_size: Optional[int] = Field(None, ge=1, description="Processing lot size")

    @field_validator("scrap_probability", "rework_probability")
    @classmethod
    def validate_probabilities(cls, v):
        """Ensure probabilities are in [0, 1]"""
        for station, prob in v.items():
            if not 0 <= prob <= 1:
                raise ValueError(f"Probability for {station} must be in [0, 1]")
        return v

class ArrivalProcess(BaseModel):
    """Defines how jobs enter the system"""
    job_type_id: str
    start_time: float = 0.0
    end_time: Optional[float] = None  # None = unlimited
    total_jobs: Optional[int] = Field(None, ge=1)  # None = unlimited

class ManufacturingModel(BaseModel):
    """Complete manufacturing simulation model"""
    name: str
    workstations: dict[str, WorkStation]
    job_types: dict[str, JobType] = Field(default_factory=dict)
    arrival_processes: list[ArrivalProcess] = Field(default_factory=list)

    simulation_time: float = Field(..., gt=0)
    warmup_time: float = Field(0, ge=0)
    random_seed: Optional[int] = None

    @field_validator('job_types')
    @classmethod
    def validate_job_routes(cls, v, info):
        """Ensure job routes reference valid workstations"""
        workstations = info.data.get('workstations', {})
        station_ids = set(workstations.keys())

        for job_type in v.values():
            invalid_stations = set(job_type.route) - station_ids
            if invalid_stations:
                raise ValueError(
                    f"Job type {job_type.id} route contains invalid stations: {invalid_stations}"
                )

            # Validate station-specific processing times
            invalid_proc = set(job_type.station_processing_times.keys()) - station_ids
            if invalid_proc:
                raise ValueError(
                    f"Job type {job_type.id} has processing times for invalid stations: {invalid_proc}"
                )

            # Validate scrap/rework stations
            invalid_scrap = set(job_type.scrap_probability.keys()) - station_ids
            invalid_rework = set(job_type.rework_probability.keys()) - station_ids
            if invalid_scrap or invalid_rework:
                raise ValueError(f"Job type {job_type.id} has invalid scrap/rework stations")

            if job_type.rework_station and job_type.rework_station not in station_ids:
                raise ValueError(f"Invalid rework_station: {job_type.rework_station}")

        return v

    @field_validator('arrival_processes')
    @classmethod
    def validate_arrivals(cls, v, info):
        """Ensure arrival processes reference valid job types"""
        job_types = info.data.get('job_types', {})
        job_type_ids = set(job_types.keys())

        for arrival in v:
            if arrival.job_type_id not in job_type_ids:
                raise ValueError(
                    f"Arrival process references invalid job type: {arrival.job_type_id}"
                )

        return v