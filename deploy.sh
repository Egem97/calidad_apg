#!/bin/bash

# Script de despliegue para PT_CALIDAD en VPS Ubuntu
# Uso: ./deploy.sh

set -e

echo "🚀 Iniciando despliegue de PT_CALIDAD..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    print_warning "Docker no está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_status "Docker instalado correctamente"
else
    print_status "Docker ya está instalado"
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose no está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose instalado correctamente"
else
    print_status "Docker Compose ya está instalado"
fi

# Verificar si el proyecto existe
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encontró docker-compose.yml. Asegúrate de estar en el directorio correcto del proyecto."
    exit 1
fi

# Parar contenedores existentes si los hay
print_status "Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null || true

# Construir y ejecutar
print_status "Construyendo y ejecutando la aplicación..."
docker-compose up -d --build

# Esperar un momento para que la aplicación se inicie
print_status "Esperando que la aplicación se inicie..."
sleep 10

# Verificar que la aplicación está funcionando
if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    print_status "✅ Aplicación desplegada correctamente!"
    print_status "🌐 Accede a tu aplicación en: http://$(curl -s ifconfig.me):8501"
else
    print_warning "La aplicación puede estar tardando en iniciarse. Verificando logs..."
    docker-compose logs --tail=20
fi

# Configurar firewall
print_status "Configurando firewall..."
sudo ufw allow 8501 2>/dev/null || true

print_status "🎉 Despliegue completado!"
print_status "Para ver los logs: docker-compose logs -f"
print_status "Para detener: docker-compose down"
print_status "Para reiniciar: docker-compose restart"
