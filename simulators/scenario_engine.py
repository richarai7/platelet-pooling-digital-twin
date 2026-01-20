"""
Scenario Modeling Engine for Platelet Pooling Digital Twin.

Enables "what-if" analysis by allowing users to adjust parameters
and compare different configurations.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DeviceConfiguration:
    """Configuration for a single device type."""
    device_type: str
    count: int
    processing_time_minutes: float
    failure_rate: float = 0.01
    cost_per_unit: float = 0.0
    floor_space_sqft: float = 0.0


@dataclass
class StaffConfiguration:
    """Staff allocation configuration."""
    technician_count: int
    efficiency_factor: float = 1.0  # 0.5 = 50% efficient, 1.0 = 100%
    cost_per_hour: float = 35.0
    shift_hours: int = 8


@dataclass
class SupplyConfiguration:
    """Input supply configuration."""
    donations_per_day: int
    units_per_donation: int = 1
    pooling_ratio: int = 4  # How many units per pooled product


@dataclass
class ConstraintConfiguration:
    """Physical and budget constraints."""
    max_floor_space_sqft: float = 500.0
    max_total_budget: float = 500000.0
    max_devices_total: int = 20
    max_staff: int = 10


@dataclass
class Scenario:
    """Complete scenario configuration."""
    id: str
    name: str
    description: str
    created_at: str
    devices: List[DeviceConfiguration]
    staff: StaffConfiguration
    supply: SupplyConfiguration
    constraints: ConstraintConfiguration
    is_baseline: bool = False


@dataclass
class ScenarioOutcome:
    """Calculated outcomes for a scenario."""
    scenario_id: str
    scenario_name: str
    
    # Process metrics
    total_process_time_minutes: float
    throughput_products_per_day: float
    cycle_time_minutes: float
    
    # Utilization metrics
    device_utilization: Dict[str, float]  # device_type -> utilization %
    staff_utilization_percent: float
    bottleneck_device: str
    
    # Resource metrics
    total_floor_space_sqft: float
    total_device_cost: float
    total_daily_staff_cost: float
    cost_per_product: float
    
    # Capacity metrics
    daily_capacity: int
    supply_utilization_percent: float
    
    # Constraint violations
    constraints_violated: List[str]
    is_feasible: bool


class ScenarioEngine:
    """
    Engine for managing and comparing scenarios.
    
    Allows users to create, save, and compare different
    configurations to optimize the platelet pooling process.
    """
    
    def __init__(self):
        self.scenarios: Dict[str, Scenario] = {}
        self.outcomes: Dict[str, ScenarioOutcome] = {}
        self._initialize_baseline()
    
    def _initialize_baseline(self):
        """Create baseline scenario with current configuration."""
        baseline = Scenario(
            id=str(uuid.uuid4()),
            name="Baseline",
            description="Current production configuration",
            created_at=datetime.now().isoformat(),
            devices=[
                DeviceConfiguration("centrifuge", 1, 15, 0.01, 50000, 25),
                DeviceConfiguration("plasma_extractor", 1, 8, 0.01, 30000, 15),
                DeviceConfiguration("macopress", 1, 10, 0.01, 40000, 20),
                DeviceConfiguration("sterile_connector", 1, 0.5, 0.005, 15000, 5),
                DeviceConfiguration("pooling_station", 1, 12, 0.01, 35000, 20),
                DeviceConfiguration("quality_control", 1, 10, 0.02, 60000, 30),
                DeviceConfiguration("labeling_station", 1, 0.25, 0.003, 10000, 5),
                DeviceConfiguration("storage_refrigerator", 1, 0, 0.001, 25000, 40),
            ],
            staff=StaffConfiguration(
                technician_count=3,
                efficiency_factor=0.85,
                cost_per_hour=35.0,
                shift_hours=8
            ),
            supply=SupplyConfiguration(
                donations_per_day=100,
                units_per_donation=1,
                pooling_ratio=4
            ),
            constraints=ConstraintConfiguration(
                max_floor_space_sqft=500,
                max_total_budget=500000,
                max_devices_total=20,
                max_staff=10
            ),
            is_baseline=True
        )
        
        self.scenarios[baseline.id] = baseline
        logger.info(f"Created baseline scenario: {baseline.id}")
    
    def create_scenario(
        self,
        name: str,
        description: str,
        devices: List[Dict],
        staff: Dict,
        supply: Dict,
        constraints: Optional[Dict] = None
    ) -> Scenario:
        """Create a new scenario."""
        scenario = Scenario(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
            devices=[DeviceConfiguration(**d) for d in devices],
            staff=StaffConfiguration(**staff),
            supply=SupplyConfiguration(**supply),
            constraints=ConstraintConfiguration(**(constraints or {})),
            is_baseline=False
        )
        
        self.scenarios[scenario.id] = scenario
        logger.info(f"Created scenario: {name} ({scenario.id})")
        return scenario
    
    def calculate_outcomes(self, scenario_id: str) -> ScenarioOutcome:
        """Calculate outcomes for a scenario."""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Calculate process time
        total_process_time = self._calculate_process_time(scenario)
        
        # Calculate throughput
        throughput = self._calculate_throughput(scenario, total_process_time)
        
        # Calculate device utilization
        device_util, bottleneck = self._calculate_device_utilization(scenario, throughput)
        
        # Calculate staff utilization
        staff_util = self._calculate_staff_utilization(scenario, total_process_time)
        
        # Calculate costs
        floor_space, device_cost, staff_cost = self._calculate_costs(scenario)
        
        # Calculate capacity
        daily_capacity, supply_util = self._calculate_capacity(scenario)
        
        # Check constraints
        violations = self._check_constraints(scenario, floor_space, device_cost)
        
        cost_per_product = (device_cost / 365 + staff_cost) / throughput if throughput > 0 else 0
        
        outcome = ScenarioOutcome(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            total_process_time_minutes=total_process_time,
            throughput_products_per_day=throughput,
            cycle_time_minutes=total_process_time / scenario.staff.technician_count,
            device_utilization=device_util,
            staff_utilization_percent=staff_util,
            bottleneck_device=bottleneck,
            total_floor_space_sqft=floor_space,
            total_device_cost=device_cost,
            total_daily_staff_cost=staff_cost,
            cost_per_product=cost_per_product,
            daily_capacity=daily_capacity,
            supply_utilization_percent=supply_util,
            constraints_violated=violations,
            is_feasible=len(violations) == 0
        )
        
        self.outcomes[scenario_id] = outcome
        logger.info(f"Calculated outcomes for {scenario.name}: {throughput:.1f} products/day")
        return outcome
    
    def _calculate_process_time(self, scenario: Scenario) -> float:
        """Calculate total process time in minutes."""
        # Sum all device processing times
        total_time = sum(d.processing_time_minutes for d in scenario.devices)
        
        # Adjust for staff efficiency
        adjusted_time = total_time / scenario.staff.efficiency_factor
        
        # Add overhead for device failures
        failure_overhead = sum(
            d.processing_time_minutes * d.failure_rate 
            for d in scenario.devices
        )
        
        return adjusted_time + failure_overhead
    
    def _calculate_throughput(self, scenario: Scenario, process_time: float) -> float:
        """Calculate daily throughput (products per day)."""
        # Minutes available per day
        minutes_per_day = scenario.staff.shift_hours * 60 * scenario.staff.technician_count
        
        # How many batches can be processed
        batches_per_day = minutes_per_day / process_time if process_time > 0 else 0
        
        # Limited by supply
        max_from_supply = scenario.supply.donations_per_day / scenario.supply.pooling_ratio
        
        return min(batches_per_day, max_from_supply)
    
    def _calculate_device_utilization(
        self, 
        scenario: Scenario, 
        throughput: float
    ) -> tuple[Dict[str, float], str]:
        """Calculate utilization % for each device type."""
        utilization = {}
        max_util = 0
        bottleneck = ""
        
        shift_minutes = scenario.staff.shift_hours * 60
        
        for device in scenario.devices:
            # Time spent processing per day
            processing_time = device.processing_time_minutes * throughput
            
            # Available time (device count * shift hours)
            available_time = shift_minutes * device.count
            
            # Utilization %
            util = (processing_time / available_time * 100) if available_time > 0 else 0
            utilization[device.device_type] = min(util, 100)
            
            if util > max_util:
                max_util = util
                bottleneck = device.device_type
        
        return utilization, bottleneck
    
    def _calculate_staff_utilization(self, scenario: Scenario, process_time: float) -> float:
        """Calculate staff utilization percentage."""
        shift_minutes = scenario.staff.shift_hours * 60
        available_minutes = shift_minutes * scenario.staff.technician_count
        
        # Assume staff is actively working during process time
        return min((process_time / available_minutes * 100), 100) if available_minutes > 0 else 0
    
    def _calculate_costs(self, scenario: Scenario) -> tuple[float, float, float]:
        """Calculate floor space, device cost, and daily staff cost."""
        floor_space = sum(d.floor_space_sqft * d.count for d in scenario.devices)
        device_cost = sum(d.cost_per_unit * d.count for d in scenario.devices)
        staff_cost = (
            scenario.staff.technician_count * 
            scenario.staff.cost_per_hour * 
            scenario.staff.shift_hours
        )
        
        return floor_space, device_cost, staff_cost
    
    def _calculate_capacity(self, scenario: Scenario) -> tuple[int, float]:
        """Calculate daily capacity and supply utilization."""
        # Theoretical max from supply
        max_from_supply = scenario.supply.donations_per_day / scenario.supply.pooling_ratio
        
        # Calculate what we can actually process
        outcome = self.outcomes.get(scenario.id)
        actual_throughput = outcome.throughput_products_per_day if outcome else max_from_supply
        
        supply_util = (actual_throughput / max_from_supply * 100) if max_from_supply > 0 else 0
        
        return int(max_from_supply), supply_util
    
    def _check_constraints(
        self, 
        scenario: Scenario, 
        floor_space: float, 
        device_cost: float
    ) -> List[str]:
        """Check if scenario violates any constraints."""
        violations = []
        
        if floor_space > scenario.constraints.max_floor_space_sqft:
            violations.append(
                f"Floor space ({floor_space:.0f} sqft) exceeds limit "
                f"({scenario.constraints.max_floor_space_sqft:.0f} sqft)"
            )
        
        if device_cost > scenario.constraints.max_total_budget:
            violations.append(
                f"Device cost (${device_cost:,.0f}) exceeds budget "
                f"(${scenario.constraints.max_total_budget:,.0f})"
            )
        
        total_devices = sum(d.count for d in scenario.devices)
        if total_devices > scenario.constraints.max_devices_total:
            violations.append(
                f"Total devices ({total_devices}) exceeds limit "
                f"({scenario.constraints.max_devices_total})"
            )
        
        if scenario.staff.technician_count > scenario.constraints.max_staff:
            violations.append(
                f"Staff count ({scenario.staff.technician_count}) exceeds limit "
                f"({scenario.constraints.max_staff})"
            )
        
        return violations
    
    def compare_scenarios(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple scenarios side-by-side."""
        if not scenario_ids:
            raise ValueError("Must provide at least one scenario ID")
        
        comparison = {
            "scenarios": [],
            "metrics": {}
        }
        
        for scenario_id in scenario_ids:
            if scenario_id not in self.scenarios:
                continue
            
            scenario = self.scenarios[scenario_id]
            outcome = self.outcomes.get(scenario_id)
            
            if not outcome:
                outcome = self.calculate_outcomes(scenario_id)
            
            comparison["scenarios"].append({
                "id": scenario.id,
                "name": scenario.name,
                "is_baseline": scenario.is_baseline,
                "outcome": asdict(outcome)
            })
        
        # Calculate improvements vs baseline
        baseline_id = next((s.id for s in self.scenarios.values() if s.is_baseline), None)
        if baseline_id and baseline_id in self.outcomes:
            baseline_outcome = self.outcomes[baseline_id]
            
            for scenario_data in comparison["scenarios"]:
                if scenario_data["id"] == baseline_id:
                    continue
                
                outcome = scenario_data["outcome"]
                improvements = {
                    "throughput_improvement_percent": (
                        (outcome["throughput_products_per_day"] - baseline_outcome.throughput_products_per_day) 
                        / baseline_outcome.throughput_products_per_day * 100
                    ) if baseline_outcome.throughput_products_per_day > 0 else 0,
                    "cost_reduction_percent": (
                        (baseline_outcome.cost_per_product - outcome["cost_per_product"]) 
                        / baseline_outcome.cost_per_product * 100
                    ) if baseline_outcome.cost_per_product > 0 else 0,
                    "staff_utilization_improvement": (
                        outcome["staff_utilization_percent"] - baseline_outcome.staff_utilization_percent
                    )
                }
                scenario_data["improvements"] = improvements
        
        return comparison
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID."""
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """List all scenarios."""
        return [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "created_at": s.created_at,
                "is_baseline": s.is_baseline,
                "has_outcome": s.id in self.outcomes
            }
            for s in self.scenarios.values()
        ]
    
    def delete_scenario(self, scenario_id: str):
        """Delete a scenario."""
        if scenario_id in self.scenarios:
            scenario = self.scenarios[scenario_id]
            if scenario.is_baseline:
                raise ValueError("Cannot delete baseline scenario")
            
            del self.scenarios[scenario_id]
            if scenario_id in self.outcomes:
                del self.outcomes[scenario_id]
            
            logger.info(f"Deleted scenario: {scenario_id}")
    
    def export_scenario(self, scenario_id: str) -> str:
        """Export scenario as JSON."""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        return json.dumps(asdict(scenario), indent=2)
    
    def import_scenario(self, json_str: str) -> Scenario:
        """Import scenario from JSON."""
        data = json.loads(json_str)
        data["id"] = str(uuid.uuid4())  # Generate new ID
        data["created_at"] = datetime.now().isoformat()
        
        scenario = Scenario(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            created_at=data["created_at"],
            devices=[DeviceConfiguration(**d) for d in data["devices"]],
            staff=StaffConfiguration(**data["staff"]),
            supply=SupplyConfiguration(**data["supply"]),
            constraints=ConstraintConfiguration(**data["constraints"]),
            is_baseline=False
        )
        
        self.scenarios[scenario.id] = scenario
        return scenario


# Example usage
if __name__ == "__main__":
    engine = ScenarioEngine()
    
    # Get baseline
    baseline_id = next(s.id for s in engine.scenarios.values() if s.is_baseline)
    baseline_outcome = engine.calculate_outcomes(baseline_id)
    
    print("\n" + "="*60)
    print("BASELINE SCENARIO")
    print("="*60)
    print(f"Throughput: {baseline_outcome.throughput_products_per_day:.1f} products/day")
    print(f"Process Time: {baseline_outcome.total_process_time_minutes:.1f} minutes")
    print(f"Staff Utilization: {baseline_outcome.staff_utilization_percent:.1f}%")
    print(f"Bottleneck: {baseline_outcome.bottleneck_device}")
    print(f"Cost per Product: ${baseline_outcome.cost_per_product:.2f}")
    print(f"Feasible: {baseline_outcome.is_feasible}")
    
    # Create optimized scenario - add 2nd centrifuge
    baseline = engine.get_scenario(baseline_id)
    optimized_devices = [asdict(d) for d in baseline.devices]
    
    # Find centrifuge and increase count
    for device in optimized_devices:
        if device["device_type"] == "centrifuge":
            device["count"] = 2
    
    optimized = engine.create_scenario(
        name="Add 2nd Centrifuge",
        description="Test impact of adding second centrifuge to reduce bottleneck",
        devices=optimized_devices,
        staff=asdict(baseline.staff),
        supply=asdict(baseline.supply),
        constraints=asdict(baseline.constraints)
    )
    
    optimized_outcome = engine.calculate_outcomes(optimized.id)
    
    print("\n" + "="*60)
    print("OPTIMIZED SCENARIO: Add 2nd Centrifuge")
    print("="*60)
    print(f"Throughput: {optimized_outcome.throughput_products_per_day:.1f} products/day "
          f"({((optimized_outcome.throughput_products_per_day - baseline_outcome.throughput_products_per_day) / baseline_outcome.throughput_products_per_day * 100):+.1f}%)")
    print(f"Process Time: {optimized_outcome.total_process_time_minutes:.1f} minutes")
    print(f"Staff Utilization: {optimized_outcome.staff_utilization_percent:.1f}%")
    print(f"Bottleneck: {optimized_outcome.bottleneck_device}")
    print(f"Cost per Product: ${optimized_outcome.cost_per_product:.2f}")
    print(f"Feasible: {optimized_outcome.is_feasible}")
    
    # Compare scenarios
    comparison = engine.compare_scenarios([baseline_id, optimized.id])
    
    print("\n" + "="*60)
    print("SCENARIO COMPARISON")
    print("="*60)
    for scenario in comparison["scenarios"]:
        print(f"\n{scenario['name']}:")
        if "improvements" in scenario:
            print(f"  Throughput improvement: {scenario['improvements']['throughput_improvement_percent']:+.1f}%")
            print(f"  Cost reduction: {scenario['improvements']['cost_reduction_percent']:+.1f}%")
