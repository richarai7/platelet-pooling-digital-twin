"""
API Backend for Scenario Modeling Frontend.

Provides REST endpoints to connect frontend to scenario engine,
staff simulator, and process orchestrator.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add simulators directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'simulators'))

from scenario_engine import ScenarioEngine
from staff_simulator import StaffSimulator
from process_orchestrator import ProcessOrchestrator
from dataclasses import asdict

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize engines
scenario_engine = ScenarioEngine()
staff_simulator = StaffSimulator(technician_count=3)


@app.route('/', methods=['GET'])
def index():
    """API information endpoint."""
    return jsonify({
        'name': 'Platelet Pooling Digital Twin API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'scenarios': '/api/scenarios',
            'baseline': '/api/baseline',
            'staff': '/api/staff/summary',
            'health': '/api/health'
        },
        'documentation': 'Access /api/health for health check'
    })


@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    """List all scenarios."""
    scenarios = scenario_engine.list_scenarios()
    return jsonify(scenarios)


@app.route('/api/scenarios', methods=['POST'])
def create_scenario():
    """Create a new scenario."""
    data = request.json
    
    try:
        scenario = scenario_engine.create_scenario(
            name=data['name'],
            description=data.get('description', ''),
            devices=data['devices'],
            staff=data['staff'],
            supply=data['supply'],
            constraints=data.get('constraints')
        )
        
        return jsonify({
            'id': scenario.id,
            'name': scenario.name,
            'created_at': scenario.created_at
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/scenarios/<scenario_id>/calculate', methods=['POST'])
def calculate_scenario(scenario_id):
    """Calculate outcomes for a scenario."""
    try:
        outcome = scenario_engine.calculate_outcomes(scenario_id)
        return jsonify(asdict(outcome))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/scenarios/<scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    """Get a specific scenario."""
    scenario = scenario_engine.get_scenario(scenario_id)
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    
    return jsonify(asdict(scenario))


@app.route('/api/scenarios/<scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id):
    """Delete a scenario."""
    try:
        scenario_engine.delete_scenario(scenario_id)
        return jsonify({'message': 'Scenario deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/scenarios/compare', methods= ['POST'])
def compare_scenarios():
    """Compare multiple scenarios."""
    data = request.json
    scenario_ids = data.get('scenario_ids', [])
    
    if not scenario_ids:
        return jsonify({'error': 'No scenario IDs provided'}), 400
    
    try:
        comparison = scenario_engine.compare_scenarios(scenario_ids)
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/staff/summary', methods=['GET'])
def get_staff_summary():
    """Get staff allocation summary."""
    summary = staff_simulator.get_staff_summary()
    return jsonify(summary)


@app.route('/api/staff/optimize', methods=['POST'])
def optimize_staffing():
    """Get staffing recommendations."""
    data = request.json
    target_throughput = data.get('target_throughput', 25)
    avg_process_time = data.get('avg_process_time_minutes', 60)
    
    optimization = staff_simulator.optimize_staffing(
        target_throughput=target_throughput,
        avg_process_time_minutes=avg_process_time
    )
    
    return jsonify(optimization)


@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    """Get baseline scenario and outcome."""
    baseline_id = next((s.id for s in scenario_engine.scenarios.values() if s.is_baseline), None)
    
    if not baseline_id:
        return jsonify({'error': 'Baseline not found'}), 404
    
    scenario = scenario_engine.get_scenario(baseline_id)
    outcome = scenario_engine.outcomes.get(baseline_id)
    
    if not outcome:
        outcome = scenario_engine.calculate_outcomes(baseline_id)
    
    return jsonify({
        'scenario': asdict(scenario),
        'outcome': asdict(outcome)
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'scenarios_count': len(scenario_engine.scenarios),
        'staff_count': len(staff_simulator.technicians)
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Scenario Modeling API Server")
    print("="*60)
    print("API available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /api/scenarios - List all scenarios")
    print("  POST /api/scenarios - Create scenario")
    print("  GET  /api/scenarios/<id> - Get scenario")
    print("  POST /api/scenarios/<id>/calculate - Calculate outcome")
    print("  POST /api/scenarios/compare - Compare scenarios")
    print("  GET  /api/baseline - Get baseline scenario")
    print("  GET  /api/staff/summary - Staff summary")
    print("  POST /api/staff/optimize - Optimize staffing")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
