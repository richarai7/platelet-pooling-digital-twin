"""
NBMS (Lab Information System) Data Simulator.

Simulates the laboratory information management system that tracks:
- Batch records and lineage
- Product tracking and inventory
- Quality test results
- Regulatory compliance
- Staff assignments
"""
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NBMSSimulator:
    """
    Simulates NBMS (Lab Information Management System) data.
    
    Generates batch records, product tracking, quality data, and
    inventory information that would come from a real NBMS.
    """
    
    def __init__(self):
        self.batches: Dict[str, Dict] = {}
        self.products: List[Dict] = []
        self.inventory: Dict[str, int] = {
            "buffy_coat_packs": 100,
            "platelet_bags": 50,
            "plasma_bags": 75,
            "pooled_products": 10
        }
        self.staff_assignments: List[Dict] = []
        
    def generate_batch_record(self, batch_id: str, donation_ids: List[str]) -> Dict[str, Any]:
        """Generate a batch record for NBMS."""
        batch_record = {
            "batch_id": batch_id,
            "created_timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "donation_ids": donation_ids,
            "number_of_units": len(donation_ids),
            "batch_type": "platelet_pooling",
            "priority": random.choice(["routine", "urgent", "stat"]),
            "technician_id": f"TECH-{random.randint(100, 999)}",
            "quality_control": {
                "pre_pool_tests_complete": False,
                "post_pool_tests_complete": False,
                "bacterial_screening": "pending",
                "visual_inspection": "pending"
            },
            "regulatory": {
                "gmp_compliant": True,
                "traceable": True,
                "documentation_complete": False
            },
            "expected_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        self.batches[batch_id] = batch_record
        logger.info(f"Created NBMS batch record: {batch_id}")
        return batch_record
    
    def update_batch_status(self, batch_id: str, status: str, updates: Dict = None) -> Dict[str, Any]:
        """Update batch status in NBMS."""
        if batch_id not in self.batches:
            logger.warning(f"Batch {batch_id} not found in NBMS")
            return {}
        
        self.batches[batch_id]["status"] = status
        self.batches[batch_id]["last_updated"] = datetime.now().isoformat()
        
        if updates:
            self.batches[batch_id].update(updates)
        
        logger.info(f"Updated batch {batch_id} status to {status}")
        return self.batches[batch_id]
    
    def generate_product_record(self, batch_id: str, product_type: str = "pooled_platelets") -> Dict[str, Any]:
        """Generate final product record."""
        product_id = f"PROD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        product = {
            "product_id": product_id,
            "batch_id": batch_id,
            "product_type": product_type,
            "volume_ml": random.randint(280, 320),
            "platelet_count": random.uniform(3.0, 5.0),  # x10^11 per unit
            "manufacturing_date": datetime.now().isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "storage_location": f"FRIDGE-{random.randint(1, 5)}-SHELF-{random.randint(1, 10)}",
            "status": "in_storage",
            "quality_tests": {
                "platelet_count_test": {
                    "result": random.uniform(800, 1200),  # x10^9/L
                    "pass": True,
                    "timestamp": datetime.now().isoformat()
                },
                "ph_test": {
                    "result": random.uniform(7.0, 7.5),
                    "pass": True,
                    "timestamp": datetime.now().isoformat()
                },
                "bacterial_screening": {
                    "result": "negative",
                    "pass": True,
                    "timestamp": datetime.now().isoformat()
                },
                "glucose_test": {
                    "result": random.uniform(250, 350),  # mg/dL
                    "pass": True,
                    "timestamp": datetime.now().isoformat()
                }
            },
            "release_status": "approved",
            "released_by": f"QC-{random.randint(100, 999)}",
            "released_timestamp": datetime.now().isoformat()
        }
        
        self.products.append(product)
        self.inventory["pooled_products"] += 1
        
        logger.info(f"Created product record: {product_id}")
        return product
    
    def get_inventory_status(self) -> Dict[str, Any]:
        """Get current inventory levels."""
        return {
            "timestamp": datetime.now().isoformat(),
            "inventory": self.inventory.copy(),
            "alerts": self._check_inventory_alerts(),
            "products_in_storage": len([p for p in self.products if p["status"] == "in_storage"]),
            "products_shipped": len([p for p in self.products if p["status"] == "shipped"]),
            "products_expired": len([p for p in self.products if p["status"] == "expired"])
        }
    
    def _check_inventory_alerts(self) -> List[str]:
        """Check for low inventory alerts."""
        alerts = []
        if self.inventory["buffy_coat_packs"] < 20:
            alerts.append("Low buffy coat pack inventory")
        if self.inventory["platelet_bags"] < 10:
            alerts.append("Low platelet bag inventory")
        if self.inventory["pooled_products"] < 5:
            alerts.append("Low finished product inventory")
        return alerts
    
    def assign_staff(self, batch_id: str, technician_id: str, role: str) -> Dict[str, Any]:
        """Assign staff to batch."""
        assignment = {
            "batch_id": batch_id,
            "technician_id": technician_id,
            "role": role,
            "assigned_timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.staff_assignments.append(assignment)
        logger.info(f"Assigned {technician_id} to batch {batch_id} as {role}")
        return assignment
    
    def record_quality_test(self, batch_id: str, test_type: str, result: Any, passed: bool) -> Dict[str, Any]:
        """Record quality control test result."""
        if batch_id not in self.batches:
            logger.warning(f"Batch {batch_id} not found")
            return {}
        
        test_record = {
            "test_type": test_type,
            "result": result,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "tested_by": f"QC-{random.randint(100, 999)}"
        }
        
        if "quality_tests" not in self.batches[batch_id]:
            self.batches[batch_id]["quality_tests"] = []
        
        self.batches[batch_id]["quality_tests"].append(test_record)
        logger.info(f"Recorded {test_type} for batch {batch_id}: {'PASS' if passed else 'FAIL'}")
        return test_record
    
    def generate_compliance_report(self, batch_id: str) -> Dict[str, Any]:
        """Generate regulatory compliance report."""
        if batch_id not in self.batches:
            return {}
        
        batch = self.batches[batch_id]
        
        report = {
            "batch_id": batch_id,
            "report_timestamp": datetime.now().isoformat(),
            "gmp_compliance": {
                "all_procedures_followed": True,
                "documentation_complete": True,
                "deviations": []
            },
            "traceability": {
                "donation_ids_recorded": len(batch.get("donation_ids", [])),
                "all_tests_documented": True,
                "chain_of_custody_maintained": True
            },
            "quality_assurance": {
                "all_tests_passed": True,
                "release_criteria_met": True,
                "approved_for_distribution": True
            },
            "generated_by": "NBMS Automated Compliance System",
            "signature": f"SIG-{random.randint(100000, 999999)}"
        }
        
        return report
    
    async def simulate_batch_lifecycle(self, batch_id: str):
        """Simulate complete NBMS tracking for a batch."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting NBMS batch lifecycle simulation: {batch_id}")
        logger.info(f"{'='*60}")
        
        # Create batch
        donation_ids = [f"DON-{random.randint(100000, 999999)}" for _ in range(4)]
        batch = self.generate_batch_record(batch_id, donation_ids)
        
        await asyncio.sleep(1)
        
        # Assign staff
        self.assign_staff(batch_id, f"TECH-{random.randint(100, 999)}", "primary_technician")
        
        await asyncio.sleep(1)
        
        # Record pre-pool tests
        self.record_quality_test(batch_id, "visual_inspection", "clear", True)
        self.record_quality_test(batch_id, "bacterial_screening_pre", "negative", True)
        
        await asyncio.sleep(2)
        
        # Update to processing
        self.update_batch_status(batch_id, "processing", {
            "quality_control": {
                "pre_pool_tests_complete": True,
                "post_pool_tests_complete": False,
                "bacterial_screening": "negative",
                "visual_inspection": "pass"
            }
        })
        
        await asyncio.sleep(3)
        
        # Record post-pool tests
        self.record_quality_test(batch_id, "platelet_count", 950, True)
        self.record_quality_test(batch_id, "ph_level", 7.2, True)
        self.record_quality_test(batch_id, "glucose_level", 300, True)
        
        await asyncio.sleep(1)
        
        # Complete batch
        self.update_batch_status(batch_id, "complete", {
            "quality_control": {
                "pre_pool_tests_complete": True,
                "post_pool_tests_complete": True,
                "bacterial_screening": "negative",
                "visual_inspection": "pass"
            },
            "regulatory": {
                "gmp_compliant": True,
                "traceable": True,
                "documentation_complete": True
            }
        })
        
        # Generate product
        product = self.generate_product_record(batch_id)
        
        # Generate compliance report
        compliance = self.generate_compliance_report(batch_id)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"NBMS batch lifecycle complete: {batch_id}")
        logger.info(f"Product ID: {product['product_id']}")
        logger.info(f"Status: {product['release_status']}")
        logger.info(f"{'='*60}\n")
        
        return {
            "batch": batch,
            "product": product,
            "compliance": compliance
        }


async def main():
    """Test NBMS simulator."""
    nbms = NBMSSimulator()
    
    # Simulate a batch
    result = await nbms.simulate_batch_lifecycle("BATCH-TEST-001")
    
    # Show inventory
    inventory = nbms.get_inventory_status()
    print("\nInventory Status:")
    print(f"  Buffy coat packs: {inventory['inventory']['buffy_coat_packs']}")
    print(f"  Pooled products: {inventory['inventory']['pooled_products']}")
    print(f"  Products in storage: {inventory['products_in_storage']}")
    
    if inventory['alerts']:
        print("\nInventory Alerts:")
        for alert in inventory['alerts']:
            print(f"  ⚠️  {alert}")


if __name__ == "__main__":
    asyncio.run(main())
