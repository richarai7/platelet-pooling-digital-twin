#!/bin/bash

# Quick start script for the Digital Twin Frontend

echo "🚀 Starting Platelet Pooling Digital Twin Frontend..."
echo ""
echo "📍 The application will open in your browser at:"
echo "   http://localhost:3001"
echo ""
echo "📱 Available Pages:"
echo "   • Dashboard (2D KPIs):     http://localhost:3001/"
echo "   • 3D Visualization:        http://localhost:3001/3d"
echo "   • Reports & Analytics:     http://localhost:3001/reports"
echo "   • Simulation Config:       http://localhost:3001/config"
echo ""
echo "🔧 The server is running in the background..."
echo "   To stop: Press Ctrl+C in the terminal running 'npm run dev'"
echo ""

# Open the 3D view directly
if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:3001/3d" &
elif command -v open > /dev/null; then
    open "http://localhost:3001/3d" &
else
    echo "Please manually open: http://localhost:3001/3d"
fi

echo "✅ Done! The 3D view should now be loading in your browser."
