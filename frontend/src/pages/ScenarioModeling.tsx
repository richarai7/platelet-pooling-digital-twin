import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Slider,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Compare,
  Save,
  Refresh
} from '@mui/icons-material';

interface DeviceConfig {
  type: string;
  count: number;
  processingTime: number;
  cost: number;
  floorSpace: number;
}

interface ScenarioConfig {
  name: string;
  devices: DeviceConfig[];
  staffCount: number;
  supplyPerDay: number;
  maxFloorSpace: number;
  maxBudget: number;
}

interface ScenarioOutcome {
  throughput: number;
  processTime: number;
  staffUtilization: number;
  bottleneck: string;
  costPerProduct: number;
  floorSpaceUsed: number;
  budgetUsed: number;
  feasible: boolean;
  violations: string[];
}

const ScenarioModeling: React.FC = () => {
  const [scenario, setScenario] = useState<ScenarioConfig>({
    name: 'New Scenario',
    devices: [
      { type: 'Centrifuge', count: 1, processingTime: 15, cost: 50000, floorSpace: 25 },
      { type: 'Plasma Extractor', count: 1, processingTime: 8, cost: 30000, floorSpace: 15 },
      { type: 'Pooling Station', count: 1, processingTime: 12, cost: 35000, floorSpace: 20 },
      { type: 'Quality Control', count: 1, processingTime: 10, cost: 60000, floorSpace: 30 },
      { type: 'Labeling Station', count: 1, processingTime: 0.25, cost: 10000, floorSpace: 5 },
    ],
    staffCount: 3,
    supplyPerDay: 100,
    maxFloorSpace: 500,
    maxBudget: 500000,
  });

  const [outcome, setOutcome] = useState<ScenarioOutcome | null>(null);
  const [baseline, setBaseline] = useState<ScenarioOutcome | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const calculateOutcome = () => {
    setIsCalculating(true);
    
    // Simulate calculation
    setTimeout(() => {
      const totalProcessTime = scenario.devices.reduce((sum, d) => sum + d.processingTime * d.count, 0);
      const totalCost = scenario.devices.reduce((sum, d) => sum + d.cost * d.count, 0);
      const totalFloorSpace = scenario.devices.reduce((sum, d) => sum + d.floorSpace * d.count, 0);
      
      const staffEfficiency = 0.85;
      const adjustedTime = totalProcessTime / staffEfficiency;
      const minutesPerDay = scenario.staffCount * 8 * 60;
      const throughput = Math.min(
        minutesPerDay / adjustedTime,
        scenario.supplyPerDay / 4 // 4 units per pooled product
      );
      
      const violations: string[] = [];
      if (totalFloorSpace > scenario.maxFloorSpace) {
        violations.push(`Floor space (${totalFloorSpace} sqft) exceeds limit (${scenario.maxFloorSpace} sqft)`);
      }
      if (totalCost > scenario.maxBudget) {
        violations.push(`Budget ($${totalCost.toLocaleString()}) exceeds limit ($${scenario.maxBudget.toLocaleString()})`);
      }
      
      const result: ScenarioOutcome = {
        throughput: Math.round(throughput * 10) / 10,
        processTime: Math.round(adjustedTime * 10) / 10,
        staffUtilization: Math.min((totalProcessTime / minutesPerDay) * 100, 100),
        bottleneck: 'Centrifuge',
        costPerProduct: throughput > 0 ? totalCost / 365 / throughput : 0,
        floorSpaceUsed: totalFloorSpace,
        budgetUsed: totalCost,
        feasible: violations.length === 0,
        violations,
      };
      
      setOutcome(result);
      if (!baseline) {
        setBaseline(result);
      }
      setIsCalculating(false);
    }, 500);
  };

  const updateDeviceCount = (index: number, value: number) => {
    const newDevices = [...scenario.devices];
    newDevices[index].count = value;
    setScenario({ ...scenario, devices: newDevices });
  };

  const updateDeviceTime = (index: number, value: number) => {
    const newDevices = [...scenario.devices];
    newDevices[index].processingTime = value;
    setScenario({ ...scenario, devices: newDevices });
  };

  const resetToBaseline = () => {
    // Reset to baseline configuration
    setScenario({
      ...scenario,
      devices: [
        { type: 'Centrifuge', count: 1, processingTime: 15, cost: 50000, floorSpace: 25 },
        { type: 'Plasma Extractor', count: 1, processingTime: 8, cost: 30000, floorSpace: 15 },
        { type: 'Pooling Station', count: 1, processingTime: 12, cost: 35000, floorSpace: 20 },
        { type: 'Quality Control', count: 1, processingTime: 10, cost: 60000, floorSpace: 30 },
        { type: 'Labeling Station', count: 1, processingTime: 0.25, cost: 10000, floorSpace: 5 },
      ],
      staffCount: 3,
      supplyPerDay: 100,
    });
  };

  const getImprovementColor = (value: number) => {
    if (value > 5) return 'success';
    if (value < -5) return 'error';
    return 'default';
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Scenario Modeling & "What-If" Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Adjust parameters to compare different configurations and optimize your platelet pooling process
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Configuration Panel */}
        <Grid item xs={12} lg={7}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Configuration Parameters</Typography>
                <Box>
                  <Button
                    startIcon={<Refresh />}
                    onClick={resetToBaseline}
                    sx={{ mr: 1 }}
                  >
                    Reset
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={calculateOutcome}
                    disabled={isCalculating}
                  >
                    Calculate Outcome
                  </Button>
                </Box>
              </Box>

              <Divider sx={{ mb: 3 }} />

              {/* Staff Configuration */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Staff Allocation
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Number of technicians: {scenario.staffCount}
                </Typography>
                <Slider
                  value={scenario.staffCount}
                  onChange={(_, value) => setScenario({ ...scenario, staffCount: value as number })}
                  min={1}
                  max={10}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              {/* Supply Configuration */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Supply Configuration
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Donations per day: {scenario.supplyPerDay}
                </Typography>
                <Slider
                  value={scenario.supplyPerDay}
                  onChange={(_, value) => setScenario({ ...scenario, supplyPerDay: value as number })}
                  min={20}
                  max={200}
                  step={10}
                  marks={[
                    { value: 20, label: '20' },
                    { value: 100, label: '100' },
                    { value: 200, label: '200' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>

              {/* Device Configuration */}
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Device Configuration
              </Typography>
              <TableContainer component={Paper} variant="outlined" sx={{ mb: 4 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Device</TableCell>
                      <TableCell align="center">Count</TableCell>
                      <TableCell align="center">Processing Time (min)</TableCell>
                      <TableCell align="right">Cost</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {scenario.devices.map((device, index) => (
                      <TableRow key={device.type}>
                        <TableCell>{device.type}</TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Slider
                              value={device.count}
                              onChange={(_, value) => updateDeviceCount(index, value as number)}
                              min={1}
                              max={5}
                              marks
                              sx={{ flexGrow: 1 }}
                              size="small"
                            />
                            <Typography variant="body2" sx={{ minWidth: 20 }}>
                              {device.count}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <TextField
                            type="number"
                            value={device.processingTime}
                            onChange={(e) => updateDeviceTime(index, parseFloat(e.target.value))}
                            size="small"
                            sx={{ width: 80 }}
                            inputProps={{ step: 0.25, min: 0.1 }}
                          />
                        </TableCell>
                        <TableCell align="right">
                          ${(device.cost * device.count).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Constraints */}
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Constraints
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="Max Floor Space (sqft)"
                    type="number"
                    value={scenario.maxFloorSpace}
                    onChange={(e) => setScenario({ ...scenario, maxFloorSpace: parseInt(e.target.value) })}
                    fullWidth
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Max Budget ($)"
                    type="number"
                    value={scenario.maxBudget}
                    onChange={(e) => setScenario({ ...scenario, maxBudget: parseInt(e.target.value) })}
                    fullWidth
                    size="small"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Panel */}
        <Grid item xs={12} lg={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Calculated Outcomes
              </Typography>

              {!outcome ? (
                <Alert severity="info">
                  Adjust parameters and click "Calculate Outcome" to see results
                </Alert>
              ) : (
                <>
                  {outcome.violations.length > 0 && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Constraint Violations:
                      </Typography>
                      {outcome.violations.map((v, i) => (
                        <Typography key={i} variant="body2">
                          • {v}
                        </Typography>
                      ))}
                    </Alert>
                  )}

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {outcome.throughput}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Products/Day
                        </Typography>
                        {baseline && outcome !== baseline && (
                          <Chip
                            label={`${((outcome.throughput - baseline.throughput) / baseline.throughput * 100).toFixed(1)}%`}
                            size="small"
                            color={getImprovementColor((outcome.throughput - baseline.throughput) / baseline.throughput * 100)}
                            sx={{ mt: 1 }}
                          />
                        )}
                      </Paper>
                    </Grid>

                    <Grid item xs={6}>
                      <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {outcome.processTime.toFixed(1)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Process Time (min)
                        </Typography>
                      </Paper>
                    </Grid>

                    <Grid item xs={6}>
                      <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {outcome.staffUtilization.toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Staff Utilization
                        </Typography>
                      </Paper>
                    </Grid>

                    <Grid item xs={6}>
                      <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          ${outcome.costPerProduct.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Cost per Product
                        </Typography>
                        {baseline && outcome !== baseline && (
                          <Chip
                            label={`${((baseline.costPerProduct - outcome.costPerProduct) / baseline.costPerProduct * 100).toFixed(1)}% savings`}
                            size="small"
                            color={getImprovementColor((baseline.costPerProduct - outcome.costPerProduct) / baseline.costPerProduct * 100)}
                            sx={{ mt: 1 }}
                          />
                        )}
                      </Paper>
                    </Grid>

                    <Grid item xs={12}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        Additional Metrics
                      </Typography>
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Bottleneck Device</TableCell>
                            <TableCell align="right">
                              <Chip label={outcome.bottleneck} size="small" color="warning" />
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Floor Space Used</TableCell>
                            <TableCell align="right">
                              {outcome.floorSpaceUsed} / {scenario.maxFloorSpace} sqft
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Budget Used</TableCell>
                            <TableCell align="right">
                              ${outcome.budgetUsed.toLocaleString()} / ${scenario.maxBudget.toLocaleString()}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </Grid>

                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                        <Button
                          variant="outlined"
                          startIcon={<Save />}
                          fullWidth
                        >
                          Save Scenario
                        </Button>
                        <Button
                          variant="outlined"
                          startIcon={<Compare />}
                          fullWidth
                        >
                          Compare
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ScenarioModeling;
