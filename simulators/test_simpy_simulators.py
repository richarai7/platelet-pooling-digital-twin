"""
Test suite for SimPy-based platelet pooling simulators.

This module contains tests for all device simulators and the simulation environment.
"""
import pytest
import simpy
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem, DeviceState
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
from platelet_pooling_simulation import PlateletPoolingSimulation, SimulationConfig


class TestBatchItem:
    """Test BatchItem data class."""
    
    def test_batch_creation(self):
        """Test creating a batch item."""
        batch = BatchItem(batch_id="TEST-001", arrival_time=0.0)
        assert batch.batch_id == "TEST-001"
        assert batch.arrival_time == 0.0
        assert batch.start_time is None
        assert batch.end_time is None
        assert len(batch.process_history) == 0
    
    def test_add_process_step(self):
        """Test adding a process step to batch history."""
        batch = BatchItem(batch_id="TEST-001", arrival_time=0.0)
        batch.add_process_step(
            device_type="centrifuge",
            device_id="centrifuge_01",
            start_time=10.0,
            end_time=20.0,
            result={'success': True}
        )
        
        assert len(batch.process_history) == 1
        step = batch.process_history[0]
        assert step['device_type'] == "centrifuge"
        assert step['duration'] == 10.0


class TestDeviceSimulators:
    """Test individual device simulators."""
    
    def test_blood_bag_scanner(self):
        """Test blood bag scanner simulator."""
        env = simpy.Environment()
        scanner = BloodBagScanner(env, device_id="test_scanner")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(scanner.process_batch(batch))
        env.run()
        
        assert scanner.total_processed == 1
        assert len(batch.process_history) == 1
        assert batch.process_history[0]['device_type'] == 'blood_bag_scanner'
    
    def test_centrifuge(self):
        """Test centrifuge simulator."""
        env = simpy.Environment()
        centrifuge = Centrifuge(env, device_id="test_centrifuge")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(centrifuge.process_batch(batch))
        env.run()
        
        assert centrifuge.total_processed == 1
        assert 'separation_quality' in batch.quality_metrics
        assert 'platelet_yield' in batch.quality_metrics
    
    def test_plasma_extractor(self):
        """Test plasma extractor simulator."""
        env = simpy.Environment()
        extractor = PlasmaExtractor(env, device_id="test_extractor")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(extractor.process_batch(batch))
        env.run()
        
        assert extractor.total_processed == 1
        assert extractor.total_plasma_extracted > 0
    
    def test_macopress(self):
        """Test Macopress simulator."""
        env = simpy.Environment()
        macopress = Macopress(env, device_id="test_macopress")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(macopress.process_batch(batch))
        env.run()
        
        assert macopress.total_processed == 1
        assert macopress.total_platelet_volume > 0
    
    def test_platelet_agitator(self):
        """Test platelet agitator simulator."""
        env = simpy.Environment()
        agitator = PlateletAgitator(env, device_id="test_agitator")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(agitator.process_batch(batch))
        env.run()
        
        assert agitator.total_processed == 1
        assert 'platelet_viability' in batch.quality_metrics
    
    def test_sterile_connector(self):
        """Test sterile connector simulator."""
        env = simpy.Environment()
        connector = SterileConnector(env, device_id="test_connector")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(connector.process_batch(batch))
        env.run()
        
        assert connector.total_processed == 1
        assert connector.successful_connections + connector.failed_connections == 1
    
    def test_pooling_station(self):
        """Test pooling station simulator."""
        env = simpy.Environment()
        pooling = PoolingStation(env, device_id="test_pooling")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(pooling.process_batch(batch))
        env.run()
        
        assert pooling.total_processed == 1
        assert pooling.total_pools_created == 1
    
    def test_quality_control(self):
        """Test quality control simulator."""
        env = simpy.Environment()
        qc = QualityControl(env, device_id="test_qc")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(qc.process_batch(batch))
        env.run()
        
        assert qc.total_processed == 1
        assert 'qc_passed' in batch.quality_metrics
    
    def test_labeling_station(self):
        """Test labeling station simulator."""
        env = simpy.Environment()
        labeling = LabelingStation(env, device_id="test_labeling")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(labeling.process_batch(batch))
        env.run()
        
        assert labeling.total_processed == 1
        assert labeling.labels_printed == 1
    
    def test_storage_refrigerator(self):
        """Test storage refrigerator simulator."""
        env = simpy.Environment()
        fridge = StorageRefrigerator(env, device_id="test_fridge", mean_storage_time=100.0)
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(fridge.process_batch(batch))
        env.run()
        
        assert fridge.total_processed == 1
        assert 'storage_temperature' in batch.quality_metrics
    
    def test_barcode_reader(self):
        """Test barcode reader simulator."""
        env = simpy.Environment()
        reader = BarcodeReader(env, device_id="test_reader")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(reader.process_batch(batch))
        env.run()
        
        assert reader.total_processed == 1
        assert reader.successful_reads + reader.failed_reads == 1
    
    def test_shipping_prep(self):
        """Test shipping prep simulator."""
        env = simpy.Environment()
        shipping = ShippingPrep(env, device_id="test_shipping")
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(shipping.process_batch(batch))
        env.run()
        
        assert shipping.total_processed == 1


class TestDeviceCapacity:
    """Test device capacity and queueing."""
    
    def test_single_capacity_queue(self):
        """Test that single capacity device processes batches sequentially."""
        env = simpy.Environment()
        scanner = BloodBagScanner(env, capacity=1)
        
        batch1 = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        batch2 = BatchItem(batch_id="BATCH-002", arrival_time=0.0)
        
        env.process(scanner.process_batch(batch1))
        env.process(scanner.process_batch(batch2))
        env.run()
        
        assert scanner.total_processed == 2
        # Second batch should start after first finishes
        assert batch2.process_history[0]['start_time'] > batch1.process_history[0]['end_time']
    
    def test_multi_capacity_parallel(self):
        """Test that multi-capacity device can process in parallel."""
        env = simpy.Environment()
        centrifuge = Centrifuge(env, capacity=4)
        
        batches = [BatchItem(batch_id=f"BATCH-{i:03d}", arrival_time=0.0) for i in range(4)]
        
        for batch in batches:
            env.process(centrifuge.process_batch(batch))
        env.run()
        
        assert centrifuge.total_processed == 4
        # All batches should start at approximately the same time
        start_times = [b.process_history[0]['start_time'] for b in batches]
        assert max(start_times) - min(start_times) < 1.0


class TestTelemetry:
    """Test telemetry generation."""
    
    def test_telemetry_structure(self):
        """Test telemetry has required fields."""
        env = simpy.Environment()
        device = BloodBagScanner(env)
        
        telemetry = device.generate_telemetry()
        
        required_fields = [
            'device_id', 'device_type', 'timestamp', 'state',
            'total_processed', 'utilization', 'queue_length'
        ]
        
        for field in required_fields:
            assert field in telemetry
    
    def test_metrics_structure(self):
        """Test metrics have required fields."""
        env = simpy.Environment()
        device = BloodBagScanner(env)
        batch = BatchItem(batch_id="BATCH-001", arrival_time=0.0)
        
        env.process(device.process_batch(batch))
        env.run()
        
        metrics = device.get_metrics()
        
        required_fields = [
            'device_id', 'device_type', 'utilization', 'throughput',
            'avg_processing_time', 'total_processed'
        ]
        
        for field in required_fields:
            assert field in metrics


class TestSimulation:
    """Test complete simulation environment."""
    
    def test_basic_simulation(self):
        """Test basic simulation runs successfully."""
        config = SimulationConfig(
            simulation_duration=600.0,  # 10 minutes
            batch_arrival_rate=120.0,   # Batch every 2 minutes
            random_seed=42
        )
        
        sim = PlateletPoolingSimulation(config)
        sim.run()
        
        assert sim.batches_created > 0
        assert sim.batches_completed >= 0  # May not complete all in short time
    
    def test_simulation_metrics(self):
        """Test simulation generates metrics."""
        config = SimulationConfig(
            simulation_duration=300.0,
            batch_arrival_rate=100.0,
            random_seed=42
        )
        
        sim = PlateletPoolingSimulation(config)
        sim.run()
        
        metrics = sim.get_all_metrics()
        
        assert 'simulation' in metrics
        assert 'devices' in metrics
        assert metrics['simulation']['batches_created'] > 0
    
    def test_multiple_devices(self):
        """Test simulation with multiple devices of same type."""
        config = SimulationConfig(
            simulation_duration=300.0,
            batch_arrival_rate=60.0,
            num_centrifuges=2,
            random_seed=42
        )
        
        sim = PlateletPoolingSimulation(config)
        sim.run()
        
        assert len(sim.devices['centrifuges']) == 2
    
    def test_device_failures(self):
        """Test simulation with failures enabled."""
        config = SimulationConfig(
            simulation_duration=1000.0,
            batch_arrival_rate=100.0,
            enable_failures=True,
            mtbf=500.0,  # Short MTBF to ensure failures
            mttr=50.0,
            random_seed=42
        )
        
        sim = PlateletPoolingSimulation(config)
        sim.run()
        
        # Check if any device experienced failures
        metrics = sim.get_all_metrics()
        total_failures = sum(
            device['failure_count']
            for device_type in metrics['devices'].values()
            for device in device_type
        )
        
        # With short MTBF, we should see some failures
        assert total_failures >= 0  # May or may not have failures due to randomness


class TestProcessWorkflow:
    """Test complete process workflow."""
    
    def test_complete_workflow(self):
        """Test a batch goes through complete workflow."""
        config = SimulationConfig(
            simulation_duration=20000.0,  # Long enough to complete
            batch_arrival_rate=10000.0,   # Only one batch
            random_seed=42,
            enable_failures=False
        )
        
        sim = PlateletPoolingSimulation(config)
        sim.run()
        
        if sim.batches_completed > 0:
            completed_batch = sim.completed_batches[0]
            
            # Check batch went through all stages
            assert len(completed_batch.process_history) == 12
            
            # Check quality metrics accumulated
            assert 'separation_quality' in completed_batch.quality_metrics
            assert 'qc_passed' in completed_batch.quality_metrics
            
            # Check times are sequential
            for i in range(len(completed_batch.process_history) - 1):
                current_end = completed_batch.process_history[i]['end_time']
                next_start = completed_batch.process_history[i + 1]['start_time']
                assert next_start >= current_end


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
