"""
Staff Allocation Simulator for Platelet Pooling Process.

Models technician assignments, labor hours, and staff utilization.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Technician:
    """Individual technician model."""
    id: str
    name: str
    skill_level: float  # 0.5 = junior, 1.0 = senior
    hourly_rate: float
    shift_hours: int = 8
    certifications: List[str] = None
    
    def __post_init__(self):
        if self.certifications is None:
            self.certifications = []


@dataclass
class StaffAssignment:
    """Assignment of staff to a specific task/device."""
    technician_id: str
    device_id: str
    batch_id: str
    task_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "active"  # active, completed, interrupted


class StaffSimulator:
    """
    Simulates staff allocation and labor tracking.
    
    Tracks technician assignments, calculates labor hours,
    and determines optimal staffing levels.
    """
    
    def __init__(self, technician_count: int = 3, shift_hours: int = 8):
        self.technicians: Dict[str, Technician] = {}
        self.assignments: List[StaffAssignment] = []
        self.shift_hours = shift_hours
        self._initialize_technicians(technician_count)
    
    def _initialize_technicians(self, count: int):
        """Initialize technician pool."""
        for i in range(count):
            skill = random.choice([0.7, 0.85, 1.0])  # Mix of skill levels
            rate = 30 + (skill * 20)  # $30-$50/hr based on skill
            
            tech = Technician(
                id=f"TECH-{i+1:03d}",
                name=f"Technician {i+1}",
                skill_level=skill,
                hourly_rate=rate,
                shift_hours=self.shift_hours,
                certifications=["platelet_processing", "quality_control"]
            )
            self.technicians[tech.id] = tech
            logger.info(f"Initialized {tech.name} (skill: {tech.skill_level:.0%}, ${tech.hourly_rate:.0f}/hr)")
    
    def assign_to_device(
        self, 
        device_id: str, 
        batch_id: str, 
        task_type: str,
        duration_minutes: float = None
    ) -> Optional[str]:
        """Assign available technician to a device."""
        # Find available technician
        available = self._find_available_technician()
        
        if not available:
            logger.warning(f"No available technician for {device_id}")
            return None
        
        assignment = StaffAssignment(
            technician_id=available.id,
            device_id=device_id,
            batch_id=batch_id,
            task_type=task_type,
            start_time=datetime.now(),
            status="active"
        )
        
        if duration_minutes:
            assignment.end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        self.assignments.append(assignment)
        logger.info(f"Assigned {available.name} to {device_id} for {task_type}")
        return available.id
    
    def complete_assignment(self, technician_id: str, batch_id: str):
        """Mark assignment as complete."""
        for assignment in self.assignments:
            if (assignment.technician_id == technician_id and 
                assignment.batch_id == batch_id and 
                assignment.status == "active"):
                assignment.end_time = datetime.now()
                assignment.status = "completed"
                logger.info(f"Completed assignment for {technician_id} on {batch_id}")
                break
    
    def _find_available_technician(self) -> Optional[Technician]:
        """Find technician with no active assignments."""
        active_techs = {
            a.technician_id for a in self.assignments 
            if a.status == "active"
        }
        
        available = [
            tech for tech_id, tech in self.technicians.items()
            if tech_id not in active_techs
        ]
        
        if not available:
            return None
        
        # Return highest skill available
        return max(available, key=lambda t: t.skill_level)
    
    def calculate_utilization(self, time_period_hours: float = 8) -> Dict[str, float]:
        """Calculate utilization % for each technician."""
        utilization = {}
        
        for tech_id, tech in self.technicians.items():
            # Calculate active time
            active_minutes = sum(
                (a.end_time - a.start_time).total_seconds() / 60
                for a in self.assignments
                if a.technician_id == tech_id and a.end_time and a.status == "completed"
            )
            
            available_minutes = time_period_hours * 60
            util = (active_minutes / available_minutes * 100) if available_minutes > 0 else 0
            utilization[tech_id] = min(util, 100)
        
        return utilization
    
    def calculate_labor_cost(self) -> Dict[str, Any]:
        """Calculate total labor cost."""
        total_cost = 0
        cost_by_tech = {}
        
        for tech_id, tech in self.technicians.items():
            # Hours worked
            hours_worked = sum(
                (a.end_time - a.start_time).total_seconds() / 3600
                for a in self.assignments
                if a.technician_id == tech_id and a.end_time and a.status == "completed"
            )
            
            cost = hours_worked * tech.hourly_rate
            cost_by_tech[tech_id] = {
                "name": tech.name,
                "hours": round(hours_worked, 2),
                "rate": tech.hourly_rate,
                "cost": round(cost, 2)
            }
            total_cost += cost
        
        return {
            "total_cost": round(total_cost, 2),
            "by_technician": cost_by_tech
        }
    
    def get_staff_summary(self) -> Dict[str, Any]:
        """Get summary of staff status."""
        active_count = len({
            a.technician_id for a in self.assignments 
            if a.status == "active"
        })
        
        utilization = self.calculate_utilization()
        avg_utilization = sum(utilization.values()) / len(utilization) if utilization else 0
        
        return {
            "total_staff": len(self.technicians),
            "active_assignments": active_count,
            "available_staff": len(self.technicians) - active_count,
            "average_utilization_percent": round(avg_utilization, 1),
            "total_assignments_completed": len([a for a in self.assignments if a.status == "completed"]),
            "technicians": [
                {
                    "id": tech.id,
                    "name": tech.name,
                    "skill_level": tech.skill_level,
                    "hourly_rate": tech.hourly_rate,
                    "utilization_percent": utilization.get(tech.id, 0)
                }
                for tech in self.technicians.values()
            ]
        }
    
    def optimize_staffing(
        self, 
        target_throughput: float, 
        avg_process_time_minutes: float
    ) -> Dict[str, Any]:
        """
        Calculate optimal staff count for target throughput.
        
        Args:
            target_throughput: Desired products per day
            avg_process_time_minutes: Average time to process one batch
            
        Returns:
            Recommendations for staffing
        """
        # Calculate required labor minutes per day
        required_minutes_per_day = target_throughput * avg_process_time_minutes
        
        # Available minutes per technician per day
        minutes_per_tech = self.shift_hours * 60
        
        # Optimal staff count (with 85% utilization target)
        optimal_count = required_minutes_per_day / (minutes_per_tech * 0.85)
        
        current_count = len(self.technicians)
        
        return {
            "current_staff": current_count,
            "optimal_staff": round(optimal_count),
            "recommendation": (
                f"Add {round(optimal_count - current_count)} technician(s)" 
                if optimal_count > current_count 
                else f"Reduce by {round(current_count - optimal_count)} technician(s)" 
                if optimal_count < current_count 
                else "Current staffing is optimal"
            ),
            "expected_utilization_percent": min(
                (current_count / optimal_count * 85) if optimal_count > 0 else 100, 
                100
            ),
            "daily_labor_cost": round(
                optimal_count * self.shift_hours * 35, 
                2
            )  # Assume avg $35/hr
        }


# Example usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("STAFF ALLOCATION SIMULATOR TEST")
    print("="*60)
    
    # Create staff simulator
    staff = StaffSimulator(technician_count=3, shift_hours=8)
    
    # Simulate some assignments
    staff.assign_to_device("centrifuge-01", "BATCH-001", "centrifuge_operation", 15)
    staff.assign_to_device("pooling-01", "BATCH-001", "pooling_operation", 12)
    staff.assign_to_device("qc-01", "BATCH-001", "quality_testing", 10)
    
    # Complete assignments
    import time
    time.sleep(1)
    staff.complete_assignment("TECH-001", "BATCH-001")
    staff.complete_assignment("TECH-002", "BATCH-001")
    
    # Get summary
    summary = staff.get_staff_summary()
    print(f"\nStaff Summary:")
    print(f"  Total Staff: {summary['total_staff']}")
    print(f"  Active Assignments: {summary['active_assignments']}")
    print(f"  Available Staff: {summary['available_staff']}")
    print(f"  Average Utilization: {summary['average_utilization_percent']}%")
    
    # Labor cost
    costs = staff.calculate_labor_cost()
    print(f"\nLabor Costs:")
    print(f"  Total: ${costs['total_cost']}")
    for tech_id, data in costs['by_technician'].items():
        print(f"  {data['name']}: {data['hours']}hrs @ ${data['rate']}/hr = ${data['cost']}")
    
    # Optimization
    optimization = staff.optimize_staffing(target_throughput=25, avg_process_time_minutes=60)
    print(f"\nStaffing Optimization (for 25 products/day):")
    print(f"  Current: {optimization['current_staff']} technicians")
    print(f"  Optimal: {optimization['optimal_staff']} technicians")
    print(f"  Recommendation: {optimization['recommendation']}")
    print(f"  Expected Utilization: {optimization['expected_utilization_percent']:.1f}%")
    print(f"  Daily Labor Cost: ${optimization['daily_labor_cost']}")
