#!/bin/bash
# Skrypt do budowania .exe na Windows z poziomu WSL
# Wymaga: Python zainstalowany na Windows i dodany do PATH

set -e

# Ścieżki
WSL_PROJECT="/home/maciek/uczelnia/pomysly/statistical_toys"
WIN_PROJECT="/mnt/d/Uczelnia/statistical_toys"
WIN_BUILD_DIR="/mnt/d/Uczelnia/statistical_toys/build"

# Kolory
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "Budowanie zabawek statystycznych dla Windows"
echo "============================================================"
echo ""

# 1. Synchronizuj projekt
echo -e "${YELLOW}[1/4] Synchronizacja projektu...${NC}"
rsync -av --delete \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    --exclude 'toys/*/dist/' \
    --exclude 'toys/*/build/' \
    --exclude '*.spec' \
    "$WSL_PROJECT/" "$WIN_PROJECT/"
echo -e "${GREEN}OK${NC}"
echo ""

# 2. Utwórz katalog build
echo -e "${YELLOW}[2/4] Tworzenie katalogu build...${NC}"
mkdir -p "$WIN_BUILD_DIR"
echo -e "${GREEN}OK${NC}"
echo ""

# 3. Zainstaluj zależności (jeśli potrzeba) i buduj każdą zabawkę
echo -e "${YELLOW}[3/4] Budowanie zabawek...${NC}"
echo ""

TOYS=("histogram" "quiz_app" "confidence_intervals")

for toy in "${TOYS[@]}"; do
    echo "--- Budowanie: $toy ---"

    # Uruchom Windows Python do buildu
    # Używamy cmd.exe z /c i cd do katalogu Windows
    cmd.exe /c "cd /d D:\\Uczelnia\\statistical_toys\\toys\\$toy && pip install -r requirements.txt -q && python build.py" 2>&1 | tail -5

    echo ""
done

# 4. Skopiuj wynikowe .exe do build/
echo -e "${YELLOW}[4/4] Kopiowanie .exe do build/...${NC}"

cp "$WIN_PROJECT/toys/histogram/dist/Histogram.exe" "$WIN_BUILD_DIR/" 2>/dev/null || echo "  Histogram.exe - nie znaleziono"
cp "$WIN_PROJECT/toys/quiz_app/dist/quiz_app.exe" "$WIN_BUILD_DIR/" 2>/dev/null || echo "  quiz_app.exe - nie znaleziono"
cp "$WIN_PROJECT/toys/confidence_intervals/dist/confidence_intervals.exe" "$WIN_BUILD_DIR/" 2>/dev/null || echo "  confidence_intervals.exe - nie znaleziono"

echo ""
echo "============================================================"
echo -e "${GREEN}Gotowe!${NC}"
echo "============================================================"
echo ""
echo "Pliki .exe znajdują się w: D:\\Uczelnia\\statistical_toys\\build\\"
ls -lh "$WIN_BUILD_DIR"/*.exe 2>/dev/null || echo "Brak plików .exe"
