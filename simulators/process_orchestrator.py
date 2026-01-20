"""
Process Orchestrator for Platelet Pooling.

Coordinates batch flow through all devices, tracks dependencies,
and identifies bottlenecks.
"""
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessStage(Enum):
    """Process stages in order."""
    SCANNING = "scanning"
    CENTRIFUGE = "centrifuge"
    PLASMA_EXTRACTION = "plasma_extraction"
    MACOPRESS = "macopress"
    AGITATION = "agitation"
    STERILE_CONNECTION = "sterile_connection"
    POOLING = "pooling"
    QUALITY_CONTROL = "quality_control"
    LABELING = "labeling"
    STORAGE = "storage"
    VERIFICATION = "verification"
    SHIPPING = "shipping"


@dataclass
class BatchStatus:
    """Status of a batch in the process."""
    batch_id: str
    current_stage: ProcessStage
    start_time: datetime
    stage_start_time: datetime
    completed_stages: List[ProcessStage] = field(default_factory=list)
    wait_times: Dict[str, float] = field(default_factory=dict)  # stage -> minutes waited
    processing_times: Dict[str, float] = field(default_factory=dict)  # stage -> minutes processed
    assigned_devices: Dict[str, str] = field(default_factory=dict)  # stage -> device_id
    quality_passed: bool = True
    status: str = "in_progress"  # in_progress, completed, failed


@dataclass
class DeviceQueue:
    """Queue for a specific device type."""
    device_type: str
    capacity: int
    queue: List[str] = field(default_factory=list)  # batch_ids waiting
    current_batch: Optional[str] = None
    
    def can_accept(self) -> bool:
        """Check if device can accept new batch."""
        return self.current_batch is None
    
    def enqueue(self, batch_id: str):
        """Add batch to queue."""
        self.queue.append(batch_id)
        logger.info(f"{self.device_type} queue: {batch_id} added (queue length: {len(self.queue)})")
    
    def dequeue(self) -> Optional[str]:
        """Get next batch from queue."""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def start_processing(self, batch_id: str):
        """Mark batch as being processed."""
        self.current_batch = batch_id
    
    def finish_processing(self):
        """Mark current batch as complete."""
        self.current_batch = None


class ProcessOrchestrator:
    """
    Orchestrates batch flow through all devices.
    
    Manages queues, tracks dependencies, identifies bottlenecks,
    and calculates process metrics.
    """
    
    # Define process flow (stage -> next stage)
    PROCESS_FLOW = {
        ProcessStage.SCANNING: ProcessStage.CENTRIFUGE,
        ProcessStage.CENTRIFUGE: ProcessStage.PLASMA_EXTRACTION,
        ProcessStage.PLASMA_EXTRACTION: ProcessStage.MACOPRESS,
        ProcessStage.MACOPRESS: ProcessStage.AGITATION,
        ProcessStage.AGITATION: ProcessStage.STERILE_CONNECTION,
        ProcessStage.STERILE_CONNECTION: ProcessStage.POOLING,
        ProcessStage.POOLING: ProcessStage.QUALITY_CONTROL,
        ProcessStage.QUALITY_CONTROL: ProcessStage.LABELING,
        ProcessStage.LABELING: ProcessStage.STORAGE,
        ProcessStage.STORAGE: ProcessStage.VERIFICATION,
        ProcessStage.VERIFICATION: ProcessStage.SHIPPING,
        ProcessStage.SHIPPING: None  # End of process
    }
    
    # Default processing times (minutes)
    DEFAULT_PROCESSING_TIMES = {
        ProcessStage.SCANNING: 2,
        ProcessStage.CENTRIFUGE: 15,
        ProcessStage.PLASMA_EXTRACTION: 8,
        ProcessStage.MACOPRESS: 10,
        ProcessStage.AGITATION: 5,
        ProcessStage.STERILE_CONNECTION: 0.5,
        ProcessStage.POOLING: 12,
        ProcessStage.QUALITY_CONTROL: 10,
        ProcessStage.LABELING: 0.25,
        ProcessStage.STORAGE: 0.1,
        ProcessStage.VERIFICATION: 1.5,
        ProcessStage.SHIPPING: 8
    }
    
    def __init__(self, device_config: Dict[str, int] = None):
        """
        Initialize orchestrator.
        
        Args:
            device_config: Dict mapping device_type -> count
        """
        self.batches: Dict[str, BatchStatus] = {}
        self.queues: Dict[ProcessStage, DeviceQueue] = {}
        self.processing_times = self.DEFAULT_PROCESSING_TIMES.copy()
        
        # Initialize queues
        config = device_config or {}
        for stage in ProcessStage:
            capacity = config.get(stage.value, 1)
            self.queues[stage] = DeviceQueue(stage.value, capacity)
        
        self.metrics = {
            "batches_started": 0,
            "batches_completed": 0,
            "batches_failed": 0,
            "total_throughput_time": 0,
            "avg_wait_time_by_stage": {},
            "bottleneck_stage": None
        }
    
    def start_batch(self, batch_id: str) -> BatchStatus:
        """Start a new batch."""
        batch = BatchStatus(
            batch_id=batch_id,
            current_stage=ProcessStage.SCANNING,
            start_time=datetime.now(),
            stage_start_time=datetime.now()
        )
        
        self.batches[batch_id] = batch
        self.queues[ProcessStage.SCANNING].enqueue(batch_id)
        self.metrics["batches_started"] += 1
        
        logger.info(f"Started batch {batch_id}")
        return batch
    
    async def process_batch_stage(self, batch_id: str) -> bool:
        """
        Process one stage for a batch.
        
        Returns True if batch continues, False if complete or failed.
        """
        batch = self.batches.get(batch_id)
        if not batch or batch.status != "in_progress":
            return False
        
        current_stage = batch.current_stage
        queue = self.queues[current_stage]
        
        # Check if device is available
        if not queue.can_accept():
            # Batch is waiting
            wait_time = (datetime.now() - batch.stage_start_time).total_seconds() / 60
            batch.wait_times[current_stage.value] = wait_time
            return True
        
        # Start processing
        queue.start_processing(batch_id)
        processing_time = self.processing_times[current_stage]
        
        logger.info(f"Batch {batch_id}: Processing {current_stage.value} ({processing_time}min)")
        
        # Simulate processing
        await asyncio.sleep(processing_time * 0.1)  # Scaled down for testing
        
        # Record processing time
        actual_time = (datetime.now() - batch.stage_start_time).total_seconds() / 60
        batch.processing_times[current_stage.value] = actual_time
        batch.completed_stages.append(current_stage)
        
        # Finish processing
        queue.finish_processing()
        
        # Move to next stage
        next_stage = self.PROCESS_FLOW[current_stage]
        
        if next_stage is None:
            # Batch complete
            batch.status = "completed"
            total_time = (datetime.now() - batch.start_time).total_seconds() / 60
            self.metrics["batches_completed"] += 1
            self.metrics["total_throughput_time"] += total_time
            
            logger.info(f"Batch {batch_id}: COMPLETED (total time: {total_time:.1f}min)")
            return False
        
        # Queue for next stage
        batch.current_stage = next_stage
        batch.stage_start_time = datetime.now()
        self.queues[next_stage].enqueue(batch_id)
        
        return True
    
    def get_bottleneck_analysis(self) -> Dict[str, Any]:
        """Identify bottleneck stages."""
        avg_wait_times = {}
        queue_lengths = {}
        utilization = {}
        
        for stage, queue in self.queues.items():
            # Calculate average wait time
            wait_times = [
                b.wait_times.get(stage.value, 0)
                for b in self.batches.values()
                if stage.value in b.wait_times
            ]
            avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
            avg_wait_times[stage.value] = avg_wait
            
            # Current queue length
            queue_lengths[stage.value] = len(queue.queue)
            
            # Utilization (simplified)
            processing_count = 1 if queue.current_batch else 0
            total_batches = len([b for b in self.batches.values() if stage in b.completed_stages])
            utilization[stage.value] = (total_batches / max(self.metrics["batches_started"], 1)) * 100
        
        # Find bottleneck (highest wait time)
        bottleneck = max(avg_wait_times.items(), key=lambda x: x[1]) if avg_wait_times else (None, 0)
        
        return {
            "bottleneck_stage": bottleneck[0],
            "bottleneck_avg_wait_minutes": bottleneck[1],
            "avg_wait_by_stage": avg_wait_times,
            "queue_lengths": queue_lengths,
            "stage_utilization": utilization
        }
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get overall process metrics."""
        completed_batches = [b for b in self.batches.values() if b.status == "completed"]
        
        avg_throughput_time = (
            self.metrics["total_throughput_time"] / len(completed_batches)
            if completed_batches else 0
        )
        
        # Calculate throughput (batches per hour)
        if completed_batches:
            time_span = (
                max(b.start_time for b in completed_batches) - 
                min(b.start_time for b in completed_batches)
            ).total_seconds() / 3600
            throughput_per_hour = len(completed_batches) / time_span if time_span > 0 else 0
        else:
            throughput_per_hour = 0
        
        bottleneck_analysis = self.get_bottleneck_analysis()
        
        return {
            "batches_started": self.metrics["batches_started"],
            "batches_completed": self.metrics["batches_completed"],
            "batches_in_progress": len([b for b in self.batches.values() if b.status == "in_progress"]),
            "batches_failed": self.metrics["batches_failed"],
            "avg_throughput_time_minutes": avg_throughput_time,
            "throughput_per_hour": throughput_per_hour,
            "throughput_per_day": throughput_per_hour * 8,  # 8-hour shift
            **bottleneck_analysis
        }
    
    def set_processing_time(self, stage: ProcessStage, minutes: float):
        """Manually adjust processing time for a stage."""
        self.processing_times[stage] = minutes
        logger.info(f"Set {stage.value} processing time to {minutes} minutes")
    
    def set_device_count(self, stage: ProcessStage, count: int):
        """Manually adjust device count for a stage."""
        self.queues[stage].capacity = count
        logger.info(f"Set {stage.value} device count to {count}")


# Example usage
async def main():
    print("\n" + "="*60)
    print("PROCESS ORCHESTRATOR TEST")
    print("="*60)
    
    # Create orchestrator
    orchestrator = ProcessOrchestrator({
        "centrifuge": 1,
        "pooling": 1,
        "quality_control": 1
    })
    
    # Start 3 batches
    for i in range(3):
        orchestrator.start_batch(f"BATCH-{i+1:03d}")
        await asyncio.sleep(0.5)
    
    # Process all batches through first few stages
    print("\nProcessing batches...")
    for _ in range(10):  # Process 10 stages
        for batch_id in list(orchestrator.batches.keys()):
            continuing = await orchestrator.process_batch_stage(batch_id)
            if not continuing:
                print(f"  Batch {batch_id} completed")
        await asyncio.sleep(0.1)
    
    # Get metrics
    metrics = orchestrator.get_process_metrics()
    
    print("\n" + "="*60)
    print("PROCESS METRICS")
    print("="*60)
    print(f"Batches Started: {metrics['batches_started']}")
    print(f"Batches Completed: {metrics['batches_completed']}")
    print(f"Batches In Progress: {metrics['batches_in_progress']}")
    print(f"Avg Throughput Time: {metrics['avg_throughput_time_minutes']:.1f} minutes")
    print(f"Throughput: {metrics['throughput_per_day']:.1f} batches/day")
    print(f"\nBottleneck: {metrics['bottleneck_stage']}")
    print(f"Bottleneck Avg Wait: {metrics['bottleneck_avg_wait_minutes']:.1f} minutes")
    
    print("\nQueue Lengths:")
    for stage, length in metrics['queue_lengths'].items():
        print(f"  {stage}: {length}")


if __name__ == "__main__":
    asyncio.run(main())
