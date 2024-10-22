# build.sh
#!/usr/bin/env bash
# Exit on error
set -o errexit

# Build React app first
cd frontend
npm install
npm run build

# Create build directory in backend if it doesn't exist
cd ../backend
mkdir -p build

# Copy React build files to Flask static directory
cp -r ../frontend/build/* ./build/

# Install Python dependencies
pip install -r requirements.txt