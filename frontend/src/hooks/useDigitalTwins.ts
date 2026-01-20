import { useState, useEffect, useCallback } from 'react'

interface DeviceTwin {
  $dtId: string
  deviceType: string
  state: string
  isProcessing: boolean
  currentBatchId?: string
  errorState?: string
  lastTelemetryTime?: string
  [key: string]: any
}

export function useDigitalTwins() {
  const [twins, setTwins] = useState<DeviceTwin[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTwins = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // In production, this would call your Azure Function API
      // which queries Azure Digital Twins
      // const response = await fetch('/api/twins')
      // const data = await response.json()

      // Mock data for development
      const mockTwins: DeviceTwin[] = [
        {
          $dtId: 'centrifuge-01',
          deviceType: 'centrifuge',
          state: 'processing',
          isProcessing: true,
          currentBatchId: 'BATCH-20260120-001',
          rpm: 2987,
          temperature: 24.2,
          vibration: 1.42,
          remainingTimeSeconds: 540,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'centrifuge-02',
          deviceType: 'centrifuge',
          state: 'idle',
          isProcessing: false,
          rpm: 0,
          temperature: 22.1,
          vibration: 0.15,
          remainingTimeSeconds: 0,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'centrifuge-03',
          deviceType: 'centrifuge',
          state: 'error',
          isProcessing: false,
          errorState: 'Excessive vibration detected',
          rpm: 0,
          temperature: 25.8,
          vibration: 3.2,
          remainingTimeSeconds: 0,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'macopress-01',
          deviceType: 'macopress',
          state: 'processing',
          isProcessing: true,
          currentBatchId: 'BATCH-20260120-002',
          pressure: 245,
          flowRate: 12.5,
          temperature: 23.5,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'macopress-02',
          deviceType: 'macopress',
          state: 'idle',
          isProcessing: false,
          pressure: 0,
          flowRate: 0,
          temperature: 22.0,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'macopress-03',
          deviceType: 'macopress',
          state: 'idle',
          isProcessing: false,
          pressure: 0,
          flowRate: 0,
          temperature: 21.8,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'agitator-01',
          deviceType: 'agitator',
          state: 'processing',
          isProcessing: true,
          currentBatchId: 'BATCH-20260119-045',
          rpm: 60,
          temperature: 22.5,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'agitator-02',
          deviceType: 'agitator',
          state: 'idle',
          isProcessing: false,
          rpm: 0,
          temperature: 22.0,
          lastTelemetryTime: new Date().toISOString()
        },
        {
          $dtId: 'agitator-03',
          deviceType: 'agitator',
          state: 'idle',
          isProcessing: false,
          rpm: 0,
          temperature: 21.9,
          lastTelemetryTime: new Date().toISOString()
        },
      ]

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setTwins(mockTwins)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch digital twins')
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTwins()

    // Poll for updates every 5 seconds (in production, use SignalR)
    const interval = setInterval(fetchTwins, 5000)
    return () => clearInterval(interval)
  }, [fetchTwins])

  return {
    twins,
    loading,
    error,
    refresh: fetchTwins
  }
}
