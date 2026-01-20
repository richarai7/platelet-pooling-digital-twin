import { useEffect, useRef, useState } from 'react'
import * as BABYLON from '@babylonjs/core'
import { useDigitalTwins } from '../hooks/useDigitalTwins'
import './Visualization3D.css'

function Visualization3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<BABYLON.Scene | null>(null)
  const deviceMeshesRef = useRef<Map<string, BABYLON.Mesh>>(new Map())
  const { twins } = useDigitalTwins()
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null)

  useEffect(() => {
    if (!canvasRef.current) return

    // Create Babylon.js engine and scene
    const engine = new BABYLON.Engine(canvasRef.current, true)
    const scene = new BABYLON.Scene(engine)
    sceneRef.current = scene

    // Set background color
    scene.clearColor = new BABYLON.Color4(0.1, 0.1, 0.1, 1)

    // Add camera
    const camera = new BABYLON.ArcRotateCamera(
      'camera',
      Math.PI / 2,
      Math.PI / 3,
      30,
      BABYLON.Vector3.Zero(),
      scene
    )
    camera.attachControl(canvasRef.current, true)
    camera.lowerRadiusLimit = 10
    camera.upperRadiusLimit = 50

    // Add lights
    const hemisphericLight = new BABYLON.HemisphericLight(
      'hemiLight',
      new BABYLON.Vector3(0, 1, 0),
      scene
    )
    hemisphericLight.intensity = 0.7

    const directionalLight = new BABYLON.DirectionalLight(
      'dirLight',
      new BABYLON.Vector3(-1, -2, -1),
      scene
    )
    directionalLight.intensity = 0.5

    // Create lab floor
    const ground = BABYLON.MeshBuilder.CreateGround(
      'ground',
      { width: 40, height: 40 },
      scene
    )
    const groundMaterial = new BABYLON.StandardMaterial('groundMat', scene)
    groundMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.2, 0.2)
    groundMaterial.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1)
    groundMaterial.wireframe = false
    ground.material = groundMaterial

    // Add grid lines for reference
    const gridLines = BABYLON.MeshBuilder.CreateLines(
      'gridLines',
      {
        points: [
          new BABYLON.Vector3(-20, 0, -20),
          new BABYLON.Vector3(20, 0, -20),
          new BABYLON.Vector3(20, 0, 20),
          new BABYLON.Vector3(-20, 0, 20),
          new BABYLON.Vector3(-20, 0, -20),
        ]
      },
      scene
    )
    gridLines.color = new BABYLON.Color3(0.5, 0.5, 0.5)

    // Create device meshes
    createLabLayout(scene, deviceMeshesRef.current)

    // Handle mesh clicks
    scene.onPointerDown = (_evt, pickResult) => {
      if (pickResult.hit && pickResult.pickedMesh) {
        const meshName = pickResult.pickedMesh.name
        if (meshName.startsWith('device-')) {
          const deviceId = meshName.replace('device-', '')
          setSelectedDevice(deviceId)
        }
      }
    }

    // Render loop
    engine.runRenderLoop(() => {
      scene.render()
    })

    // Handle window resize
    const handleResize = () => {
      engine.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      scene.dispose()
      engine.dispose()
    }
  }, [])

  // Update device states based on digital twin data
  useEffect(() => {
    if (!twins || !sceneRef.current) return

    twins.forEach(twin => {
      const mesh = deviceMeshesRef.current.get(twin.$dtId)
      if (mesh && mesh.material) {
        const material = mesh.material as BABYLON.StandardMaterial
        
        // Update color based on state
        switch (twin.state) {
          case 'idle':
            material.emissiveColor = new BABYLON.Color3(0.3, 0.3, 0.3)
            break
          case 'processing':
            material.emissiveColor = new BABYLON.Color3(0, 0.5, 1)
            // Add pulsing animation
            const time = Date.now() * 0.001
            const pulse = 0.5 + 0.5 * Math.sin(time * 2)
            material.emissiveColor = new BABYLON.Color3(0, 0.5 * pulse, pulse)
            break
          case 'error':
            material.emissiveColor = new BABYLON.Color3(1, 0, 0)
            break
          default:
            material.emissiveColor = new BABYLON.Color3(0.3, 0.3, 0.3)
        }
      }
    })
  }, [twins])

  return (
    <div className="visualization-3d">
      <div className="page-header">
        <h2>3D Lab Visualization</h2>
        <p>Interactive view of the platelet pooling lab</p>
      </div>

      <div className="viz-container">
        <canvas ref={canvasRef} className="babylon-canvas" />
        
        {selectedDevice && (
          <div className="device-details-panel">
            <h3>Device Details</h3>
            <button 
              className="close-btn"
              onClick={() => setSelectedDevice(null)}
            >
              ✕
            </button>
            <div className="details-content">
              {twins?.find(t => t.$dtId === selectedDevice) && (
                <DeviceDetails 
                  device={twins.find(t => t.$dtId === selectedDevice)!} 
                />
              )}
            </div>
          </div>
        )}

        <div className="controls-panel">
          <h4>Controls</h4>
          <ul>
            <li>🖱️ Left click + drag: Rotate view</li>
            <li>🖱️ Right click + drag: Pan view</li>
            <li>🖱️ Scroll: Zoom in/out</li>
            <li>🖱️ Click device: View details</li>
          </ul>
          <div className="legend">
            <h4>Status Colors</h4>
            <div className="legend-item">
              <span className="color-box idle"></span> Idle
            </div>
            <div className="legend-item">
              <span className="color-box processing"></span> Processing
            </div>
            <div className="legend-item">
              <span className="color-box error"></span> Error
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper function to create lab layout with device positions
function createLabLayout(
  scene: BABYLON.Scene,
  deviceMeshes: Map<string, BABYLON.Mesh>
) {
  // Device positions in lab (x, z coordinates)
  const devicePositions = [
    { id: 'centrifuge-01', type: 'centrifuge', x: -8, z: 8 },
    { id: 'centrifuge-02', type: 'centrifuge', x: -8, z: 4 },
    { id: 'centrifuge-03', type: 'centrifuge', x: -8, z: 0 },
    { id: 'macopress-01', type: 'macopress', x: 0, z: 8 },
    { id: 'macopress-02', type: 'macopress', x: 0, z: 4 },
    { id: 'macopress-03', type: 'macopress', x: 0, z: 0 },
    { id: 'agitator-01', type: 'agitator', x: 8, z: 8 },
    { id: 'agitator-02', type: 'agitator', x: 8, z: 4 },
    { id: 'agitator-03', type: 'agitator', x: 8, z: 0 },
  ]

  devicePositions.forEach(pos => {
    let mesh: BABYLON.Mesh

    // Create different shapes for different device types
    switch (pos.type) {
      case 'centrifuge':
        mesh = BABYLON.MeshBuilder.CreateCylinder(
          `device-${pos.id}`,
          { height: 3, diameter: 2 },
          scene
        )
        break
      case 'macopress':
        mesh = BABYLON.MeshBuilder.CreateBox(
          `device-${pos.id}`,
          { width: 2, height: 2.5, depth: 2 },
          scene
        )
        break
      case 'agitator':
        mesh = BABYLON.MeshBuilder.CreateSphere(
          `device-${pos.id}`,
          { diameter: 2 },
          scene
        )
        break
      default:
        mesh = BABYLON.MeshBuilder.CreateBox(
          `device-${pos.id}`,
          { size: 2 },
          scene
        )
    }

    // Position the mesh
    mesh.position = new BABYLON.Vector3(pos.x, 1.5, pos.z)

    // Create material
    const material = new BABYLON.StandardMaterial(`${pos.id}-mat`, scene)
    material.diffuseColor = new BABYLON.Color3(0.4, 0.4, 0.4)
    material.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2)
    material.emissiveColor = new BABYLON.Color3(0.2, 0.2, 0.2)
    mesh.material = material

    // Add label
    createDeviceLabel(mesh, pos.id, scene)

    // Store mesh reference
    deviceMeshes.set(pos.id, mesh)
  })
}

// Helper to create text label for device
function createDeviceLabel(
  mesh: BABYLON.Mesh,
  label: string,
  scene: BABYLON.Scene
) {
  const plane = BABYLON.MeshBuilder.CreatePlane(
    `label-${label}`,
    { size: 2 },
    scene
  )
  plane.position = mesh.position.clone()
  plane.position.y += 2.5
  plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL

  const material = new BABYLON.StandardMaterial(`labelMat-${label}`, scene)
  material.diffuseColor = new BABYLON.Color3(1, 1, 1)
  material.emissiveColor = new BABYLON.Color3(0.5, 0.5, 0.5)
  plane.material = material

  // Note: For actual text, you'd use BABYLON.GUI.AdvancedDynamicTexture
  // This is a placeholder
}

// Device details component
function DeviceDetails({ device }: { device: any }) {
  return (
    <div className="device-info">
      <p><strong>ID:</strong> {device.$dtId}</p>
      <p><strong>Type:</strong> {device.deviceType}</p>
      <p>
        <strong>Status:</strong>{' '}
        <span className={`status-badge status-${device.state}`}>
          {device.state}
        </span>
      </p>
      {device.isProcessing && (
        <p><strong>Batch:</strong> {device.currentBatchId}</p>
      )}
      {device.rpm !== undefined && (
        <p><strong>RPM:</strong> {device.rpm.toFixed(1)}</p>
      )}
      {device.temperature !== undefined && (
        <p><strong>Temperature:</strong> {device.temperature.toFixed(1)}°C</p>
      )}
      {device.errorState && (
        <p className="error-text"><strong>Error:</strong> {device.errorState}</p>
      )}
    </div>
  )
}

export default Visualization3D
