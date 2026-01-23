"""
Platelet Pooling Process Simulation Environment.

This module orchestrates the complete platelet pooling workflow using SimPy,
coordinating all 12 devices and managing batch flow through the process.
"""
import simpy
import random
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from simpy_core.simpy_base import BatchItem
from simpy_devices import (
    BloodBagScanner,
    Centrifuge,
    PlasmaExtractor,
    Macopress,
    PlateletAgitator,
    SterileConnector,
    PoolingStation,
    QualityControl,
    LabelingStation,
    StorageRefrigerator,
    BarcodeReader,
    ShippingPrep
)


@dataclass
class SimulationConfig:
    """Configuration for platelet pooling simulation."""
    # Simulation parameters
    simulation_duration: float = 28800.0  # 8 hours in seconds
    batch_arrival_rate: float = 300.0  # New batch every 5 minutes
    random_seed: Optional[int] = None
    
    # Device counts
    num_scanners: int = 1
    num_centrifuges: int = 2
    num_plasma_extractors: int = 1
    num_macopresses: int = 1
    num_agitators: int = 1
    num_sterile_connectors: int = 1
    num_pooling_stations: int = 1
    num_qc_devices: int = 1
    num_labeling_stations: int = 1
    num_refrigerators: int = 1
    num_barcode_readers: int = 1
    num_shipping_prep: int = 1
    
    # Device reliability (optional)
    enable_failures: bool = False
    mtbf: float = 14400.0  # Mean time between failures (4 hours)
    mttr: float = 1800.0   # Mean time to repair (30 minutes)


class PlateletPoolingSimulation:
    """
    Main simulation class for the platelet pooling digital twin.
    
    This class creates and manages all devices, orchestrates batch flow,
    and collects metrics from the simulation.
    """
    
    def __init__(self, config: SimulationConfig = None):
        """
        Initialize the platelet pooling simulation.
        
        Args:
            config: Simulation configuration (uses defaults if not provided)
        """
        self.config = config or SimulationConfig()
        
        # Set random seed for reproducibility
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
        
        # Create SimPy environment
        self.env = simpy.Environment()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PlateletPoolingSimulation')
        
        # Initialize devices
        self.devices = {}
        self._initialize_devices()
        
        # Batch tracking
        self.batches_created = 0
        self.batches_completed = 0
        self.completed_batches: List[BatchItem] = []
        self.failed_batches: List[BatchItem] = []
        
        # Stores for batch queues between stages
        self.batch_queue = simpy.Store(self.env)
        
    def _initialize_devices(self):
        """Initialize all device simulators."""
        # Determine failure parameters
        mtbf = self.config.mtbf if self.config.enable_failures else None
        mttr = self.config.mttr if self.config.enable_failures else None
        
        # Blood Bag Scanners
        self.devices['scanners'] = [
            BloodBagScanner(self.env, f"scanner_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_scanners)
        ]
        
        # Centrifuges
        self.devices['centrifuges'] = [
            Centrifuge(self.env, f"centrifuge_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_centrifuges)
        ]
        
        # Plasma Extractors
        self.devices['plasma_extractors'] = [
            PlasmaExtractor(self.env, f"plasma_extractor_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_plasma_extractors)
        ]
        
        # Macopresses
        self.devices['macopresses'] = [
            Macopress(self.env, f"macopress_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_macopresses)
        ]
        
        # Platelet Agitators
        self.devices['agitators'] = [
            PlateletAgitator(self.env, f"agitator_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_agitators)
        ]
        
        # Sterile Connectors
        self.devices['sterile_connectors'] = [
            SterileConnector(self.env, f"sterile_connector_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_sterile_connectors)
        ]
        
        # Pooling Stations
        self.devices['pooling_stations'] = [
            PoolingStation(self.env, f"pooling_station_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_pooling_stations)
        ]
        
        # Quality Control
        self.devices['qc_devices'] = [
            QualityControl(self.env, f"qc_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_qc_devices)
        ]
        
        # Labeling Stations
        self.devices['labeling_stations'] = [
            LabelingStation(self.env, f"labeling_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_labeling_stations)
        ]
        
        # Storage Refrigerators
        self.devices['refrigerators'] = [
            StorageRefrigerator(self.env, f"refrigerator_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_refrigerators)
        ]
        
        # Barcode Readers
        self.devices['barcode_readers'] = [
            BarcodeReader(self.env, f"barcode_reader_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_barcode_readers)
        ]
        
        # Shipping Prep
        self.devices['shipping_prep'] = [
            ShippingPrep(self.env, f"shipping_{i+1}", mtbf=mtbf, mttr=mttr)
            for i in range(self.config.num_shipping_prep)
        ]
        
        self.logger.info("Initialized all devices successfully")
    
    def batch_generator(self):
        """
        SimPy process that generates new batches arriving at the system.
        """
        while True:
            # Wait for next batch arrival
            inter_arrival_time = random.expovariate(1.0 / self.config.batch_arrival_rate)
            yield self.env.timeout(inter_arrival_time)
            
            # Create new batch
            self.batches_created += 1
            batch = BatchItem(
                batch_id=f"BATCH-{self.batches_created:05d}",
                arrival_time=self.env.now
            )
            
            self.logger.info(f"New batch {batch.batch_id} arrived at {self.env.now:.2f}")
            
            # Start batch processing workflow
            self.env.process(self.process_batch(batch))
    
    def process_batch(self, batch: BatchItem):
        """
        SimPy process for a complete batch workflow through all devices.
        
        Args:
            batch: BatchItem to process through the workflow
        """
        try:
            # Stage 1: Blood Bag Scanner
            scanner = random.choice(self.devices['scanners'])
            yield from scanner.process_batch(batch)
            
            # Stage 2: Centrifuge
            centrifuge = random.choice(self.devices['centrifuges'])
            yield from centrifuge.process_batch(batch)
            
            # Stage 3: Plasma Extractor
            extractor = random.choice(self.devices['plasma_extractors'])
            yield from extractor.process_batch(batch)
            
            # Stage 4: Macopress
            macopress = random.choice(self.devices['macopresses'])
            yield from macopress.process_batch(batch)
            
            # Stage 5: Platelet Agitator
            agitator = random.choice(self.devices['agitators'])
            yield from agitator.process_batch(batch)
            
            # Stage 6: Sterile Connector
            connector = random.choice(self.devices['sterile_connectors'])
            yield from connector.process_batch(batch)
            
            # Stage 7: Pooling Station
            pooling = random.choice(self.devices['pooling_stations'])
            yield from pooling.process_batch(batch)
            
            # Stage 8: Quality Control
            qc = random.choice(self.devices['qc_devices'])
            yield from qc.process_batch(batch)
            
            # Check if QC passed
            if not batch.quality_metrics.get('qc_passed', False):
                self.logger.warning(f"Batch {batch.batch_id} failed QC - discarded")
                self.failed_batches.append(batch)
                return
            
            # Stage 9: Labeling Station
            labeling = random.choice(self.devices['labeling_stations'])
            yield from labeling.process_batch(batch)
            
            # Stage 10: Storage Refrigerator
            fridge = random.choice(self.devices['refrigerators'])
            yield from fridge.process_batch(batch)
            
            # Stage 11: Barcode Reader
            reader = random.choice(self.devices['barcode_readers'])
            yield from reader.process_batch(batch)
            
            # Stage 12: Shipping Prep
            shipping = random.choice(self.devices['shipping_prep'])
            yield from shipping.process_batch(batch)
            
            # Mark as completed
            batch.end_time = self.env.now
            self.batches_completed += 1
            self.completed_batches.append(batch)
            
            total_time = batch.end_time - batch.arrival_time
            self.logger.info(
                f"Batch {batch.batch_id} completed at {self.env.now:.2f} "
                f"(total time: {total_time:.2f}s, {total_time/60:.2f} min)"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing batch {batch.batch_id}: {str(e)}")
            self.failed_batches.append(batch)
    
    def run(self):
        """Run the simulation."""
        self.logger.info(f"Starting simulation for {self.config.simulation_duration}s")
        
        # Start batch generator
        self.env.process(self.batch_generator())
        
        # Run simulation
        self.env.run(until=self.config.simulation_duration)
        
        self.logger.info("Simulation completed")
        self._print_summary()
    
    def _print_summary(self):
        """Print simulation summary and metrics."""
        print("\n" + "=" * 80)
        print("SIMULATION SUMMARY")
        print("=" * 80)
        print(f"Simulation Time: {self.env.now:.2f}s ({self.env.now/3600:.2f} hours)")
        print(f"Batches Created: {self.batches_created}")
        print(f"Batches Completed: {self.batches_completed}")
        print(f"Batches Failed: {len(self.failed_batches)}")
        print(f"Completion Rate: {self.batches_completed / max(1, self.batches_created) * 100:.1f}%")
        
        if self.completed_batches:
            cycle_times = [b.end_time - b.arrival_time for b in self.completed_batches]
            avg_cycle_time = sum(cycle_times) / len(cycle_times)
            print(f"Average Cycle Time: {avg_cycle_time:.2f}s ({avg_cycle_time/60:.2f} min)")
        
        print("\n" + "-" * 80)
        print("DEVICE UTILIZATION")
        print("-" * 80)
        
        for device_type, device_list in self.devices.items():
            for device in device_list:
                metrics = device.get_metrics()
                print(f"{device.device_id:30s} - "
                      f"Util: {metrics['utilization']*100:5.1f}% | "
                      f"Processed: {metrics['total_processed']:4d} | "
                      f"Failures: {metrics['failure_count']:2d}")
        
        print("=" * 80 + "\n")
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics from all devices.
        
        Returns:
            Dictionary containing all device metrics and simulation statistics
        """
        metrics = {
            'simulation': {
                'duration': self.env.now,
                'batches_created': self.batches_created,
                'batches_completed': self.batches_completed,
                'batches_failed': len(self.failed_batches),
                'completion_rate': self.batches_completed / max(1, self.batches_created)
            },
            'devices': {}
        }
        
        for device_type, device_list in self.devices.items():
            metrics['devices'][device_type] = [
                device.get_metrics() for device in device_list
            ]
        
        return metrics
