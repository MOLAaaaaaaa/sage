#!/bin/bash
# SeismicX Quick Start Script
# This script demonstrates how to use the seismic analysis skills

set -e  # Exit on error

echo "=========================================="
echo "SeismicX - Quick Start Guide"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required files exist
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"

    if [ ! -d "pnsn" ]; then
        echo -e "${RED}Error: pnsn directory not found${NC}"
        exit 1
    fi

    if [ ! -f "pnsn/pickers/pnsn.v3.jit" ]; then
        echo -e "${RED}Error: Model file not found: pnsn/pickers/pnsn.v3.jit${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Requirements check passed${NC}"
    echo ""
}

# Check Python dependencies
check_python_deps() {
    echo -e "${YELLOW}Checking Python dependencies...${NC}"

    python3 -c "import torch" 2>/dev/null || {
        echo -e "${RED}Error: PyTorch not installed${NC}"
        echo "Install with: pip install torch"
        exit 1
    }

    python3 -c "import obspy" 2>/dev/null || {
        echo -e "${RED}Error: ObsPy not installed${NC}"
        echo "Install with: pip install obspy"
        exit 1
    }

    echo -e "${GREEN}✓ Python dependencies OK${NC}"
    echo ""
}

# Show usage examples
show_examples() {
    echo -e "${YELLOW}=== Usage Examples ===${NC}"
    echo ""

    echo "1. Phase Picking (CLI):"
    echo "   python seismic_cli.py pick \\"
    echo "       -i pnsn/data/waveform \\"
    echo "       -o results/test_picks \\"
    echo "       -m pnsn/pickers/pnsn.v3.jit \\"
    echo "       -d cpu"
    echo ""

    echo "2. Phase Association (FastLink):"
    echo "   python seismic_cli.py associate \\"
    echo "       -i results/test_picks.txt \\"
    echo "       -o results/test_events.txt \\"
    echo "       -s pnsn/data/stations.txt \\"
    echo "       -m fastlink"
    echo ""

    echo "3. Polarity Analysis:"
    echo "   python seismic_cli.py polarity \\"
    echo "       -i results/test_picks.txt \\"
    echo "       -w pnsn/data/waveform \\"
    echo "       -o results/test_polarity.txt"
    echo ""

    echo "4. Start Web Interface:"
    echo "   cd web_app && python app.py --port 5000"
    echo ""
}

# Create sample station file if not exists
create_sample_station_file() {
    if [ ! -f "pnsn/data/stations.txt" ]; then
        echo -e "${YELLOW}Creating sample station file...${NC}"
        cat > pnsn/data/stations.txt << EOF
SC A0801 00 104.5000 31.5000 1500.0
SC A0802 00 104.6000 31.6000 1600.0
SC A0803 00 104.7000 31.7000 1700.0
EOF
        echo -e "${GREEN}✓ Created: pnsn/data/stations.txt${NC}"
        echo ""
    fi
}

# Main execution
main() {
    check_requirements
    check_python_deps
    create_sample_station_file
    show_examples

    echo -e "${GREEN}=========================================="
    echo "Quick start complete!"
    echo "==========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  • Read SKILLS_README.md for detailed documentation"
    echo "  • Check individual skill docs in .lingma/skills/"
    echo "  • Try the example commands above"
    echo ""
}

# Run main function
main
