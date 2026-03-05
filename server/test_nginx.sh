#!/bin/bash
# Script de test pour vérifier que le serveur fonctionne correctement derrière Nginx

BASE_URL="${1:-http://localhost}"
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m' # No Color

echo "=========================================="
echo "Test du Serveur Capteur derrière Nginx"
echo "=========================================="
echo "URL de base: $BASE_URL"
echo ""

# Function to test an endpoint
test_endpoint() {
    local url=$1
    local expected_code=$2
    local description=$3
    
    echo -n "Test: $description ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${COLOR_GREEN}✓ PASS${COLOR_NC} (HTTP $response)"
        return 0
    else
        echo -e "${COLOR_RED}✗ FAIL${COLOR_NC} (Expected: $expected_code, Got: $response)"
        return 1
    fi
}

# Function to test JSON endpoint
test_json_endpoint() {
    local url=$1
    local description=$2
    
    echo -n "Test: $description ... "
    
    response=$(curl -s "$url" 2>/dev/null)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$http_code" = "200" ] && [ ! -z "$response" ]; then
        echo -e "${COLOR_GREEN}✓ PASS${COLOR_NC}"
        echo "  Response: $response"
        return 0
    else
        echo -e "${COLOR_RED}✗ FAIL${COLOR_NC} (HTTP $http_code)"
        return 1
    fi
}

passed=0
failed=0

echo "Tests de base:"
echo "----------------------------------------"

# Test 1: Health check
if test_json_endpoint "$BASE_URL/capture/health" "Health check"; then
    ((passed++))
else
    ((failed++))
fi

# Test 2: Root (should redirect to login or show page)
if test_endpoint "$BASE_URL/capture/" "200|302" "Page d'accueil (/capture/)"; then
    ((passed++))
else
    ((failed++))
fi

# Test 3: Login page
if test_endpoint "$BASE_URL/capture/login" "200" "Page de login"; then
    ((passed++))
else
    ((failed++))
fi

# Test 4: Redirection /capture -> /capture/
echo -n "Test: Redirection /capture -> /capture/ ... "
redirect=$(curl -s -o /dev/null -w "%{redirect_url}" "$BASE_URL/capture" 2>/dev/null)
if [[ "$redirect" == *"/capture/" ]]; then
    echo -e "${COLOR_GREEN}✓ PASS${COLOR_NC}"
    ((passed++))
else
    echo -e "${COLOR_RED}✗ FAIL${COLOR_NC} (Redirect to: $redirect)"
    ((failed++))
fi

# Test 5: Upload endpoint (should return 400 without data, not 404)
echo -n "Test: Upload endpoint ... "
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/capture/upload" 2>/dev/null)
if [ "$response" = "400" ]; then
    echo -e "${COLOR_GREEN}✓ PASS${COLOR_NC} (HTTP 400 - Endpoint exists)"
    ((passed++))
else
    echo -e "${COLOR_RED}✗ FAIL${COLOR_NC} (Expected: 400, Got: $response)"
    ((failed++))
fi

echo ""
echo "Tests avancés (optionnels):"
echo "----------------------------------------"

# Test 6: Check if Nginx is stripping /capture prefix
echo -n "Test: Vérification logs Flask ... "
echo -e "${COLOR_YELLOW}MANUEL${COLOR_NC}"
echo "  Vérifiez les logs: sudo journalctl -u capteur -n 20"
echo "  Vous devriez voir: \"GET /login\" et NON \"GET /capture/login\""

# Test 7: Test with a real image upload
echo ""
echo -n "Test: Upload d'une image réelle ... "
if command -v convert &> /dev/null; then
    # Create a test image
    convert -size 100x100 xc:blue /tmp/test_capteur.png 2>/dev/null
    
    response=$(curl -s \
        -F "image=@/tmp/test_capteur.png" \
        -F "client_id=test_client" \
        -F "monitor_id=0" \
        "$BASE_URL/capture/upload" 2>/dev/null)
    
    if [[ "$response" == *"success"* ]]; then
        echo -e "${COLOR_GREEN}✓ PASS${COLOR_NC}"
        echo "  Response: $response"
        ((passed++))
    else
        echo -e "${COLOR_RED}✗ FAIL${COLOR_NC}"
        echo "  Response: $response"
        ((failed++))
    fi
    
    rm -f /tmp/test_capteur.png
else
    echo -e "${COLOR_YELLOW}SKIP${COLOR_NC} (ImageMagick non installé)"
fi

# Summary
echo ""
echo "=========================================="
echo "Résumé"
echo "=========================================="
echo -e "Tests passés:  ${COLOR_GREEN}$passed${COLOR_NC}"
echo -e "Tests échoués: ${COLOR_RED}$failed${COLOR_NC}"

if [ $failed -eq 0 ]; then
    echo ""
    echo -e "${COLOR_GREEN}✓ Tous les tests sont passés!${COLOR_NC}"
    echo "Le serveur fonctionne correctement derrière Nginx."
    exit 0
else
    echo ""
    echo -e "${COLOR_RED}✗ Certains tests ont échoué.${COLOR_NC}"
    echo ""
    echo "Actions de dépannage:"
    echo "1. Vérifiez nginx.conf (trailing slashes)"
    echo "2. Vérifiez que APPLICATION_ROOT n'est pas défini dans app.py"
    echo "3. Rechargez Nginx: sudo systemctl reload nginx"
    echo "4. Redémarrez l'app: sudo systemctl restart capteur"
    echo "5. Consultez: server/FIX_404.md"
    exit 1
fi
