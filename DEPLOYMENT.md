# 🚀 Guía de Despliegue en VPS Ubuntu

Esta guía te ayudará a desplegar tu aplicación PT_CALIDAD en un VPS Ubuntu en la nube.

## 📋 Requisitos Previos

- VPS Ubuntu 20.04 o superior
- Acceso SSH al servidor
- Dominio (opcional, pero recomendado)

## 🛠️ Pasos de Despliegue

### 1. Conectar al VPS

```bash
ssh usuario@tu-vps-ip
```

### 2. Preparar el Sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y curl wget git unzip
```

### 3. Subir el Código

**Opción A: Clonar desde Git (Recomendado)**
```bash
git clone https://github.com/tu-usuario/PT_CALIDAD.git
cd PT_CALIDAD
```

**Opción B: Subir archivos manualmente**
```bash
# Desde tu máquina local
scp -r /c/Proyectos/PT_CALIDAD usuario@tu-vps-ip:/home/usuario/
```

### 4. Desplegar con Docker (Recomendado)

```bash
# Dar permisos de ejecución al script
chmod +x deploy.sh

# Ejecutar el script de despliegue automático
./deploy.sh
```

**O manualmente:**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Construir y ejecutar
docker-compose up -d --build
```

### 5. Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Abrir puertos necesarios
sudo ufw allow ssh
sudo ufw allow 8501
sudo ufw allow 80
sudo ufw allow 443

# Verificar estado
sudo ufw status
```

### 6. Configurar Nginx (Opcional pero recomendado)

```bash
# Instalar Nginx
sudo apt install nginx -y

# Copiar configuración
sudo cp nginx-config.conf /etc/nginx/sites-available/pt-calidad

# Editar configuración (cambiar server_name)
sudo nano /etc/nginx/sites-available/pt-calidad

# Activar sitio
sudo ln -s /etc/nginx/sites-available/pt-calidad /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remover sitio por defecto

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 7. Configurar SSL (Opcional)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Comandos Útiles

### Verificar Estado
```bash
# Ver contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Verificar que la app responde
curl http://localhost:8501/_stcore/health
```

### Mantenimiento
```bash
# Reiniciar aplicación
docker-compose restart

# Actualizar aplicación
git pull
docker-compose up -d --build

# Detener aplicación
docker-compose down

# Ver uso de recursos
docker stats
```

### Backup
```bash
# Crear backup de datos
docker-compose exec pt-calidad tar -czf /app/backup-$(date +%Y%m%d).tar.gz /app/data

# Restaurar backup
docker-compose exec pt-calidad tar -xzf /app/backup-YYYYMMDD.tar.gz -C /app/
```

## 🌐 Acceso a la Aplicación

- **Directo**: `http://tu-vps-ip:8501`
- **Con Nginx**: `http://tu-vps-ip` o `http://tu-dominio.com`
- **Con SSL**: `https://tu-dominio.com`

## 🔍 Solución de Problemas

### La aplicación no responde
```bash
# Verificar logs
docker-compose logs -f

# Verificar puertos
sudo netstat -tlnp | grep 8501

# Reiniciar contenedor
docker-compose restart
```

### Error de permisos
```bash
# Dar permisos al usuario
sudo usermod -aG docker $USER
newgrp docker
```

### Problemas de memoria
```bash
# Verificar uso de memoria
free -h
docker system prune -a  # Limpiar Docker
```

## 📊 Monitoreo

### Configurar monitoreo básico
```bash
# Instalar htop para monitoreo
sudo apt install htop -y

# Ver procesos en tiempo real
htop
```

### Logs del sistema
```bash
# Ver logs de Docker
sudo journalctl -u docker.service

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 Seguridad

### Recomendaciones básicas
1. Cambiar puerto SSH por defecto
2. Usar claves SSH en lugar de contraseñas
3. Configurar firewall (UFW)
4. Mantener el sistema actualizado
5. Usar SSL/HTTPS
6. Hacer backups regulares

### Configurar fail2ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📞 Soporte

Si tienes problemas durante el despliegue:

1. Revisar logs: `docker-compose logs -f`
2. Verificar configuración: `docker-compose config`
3. Verificar conectividad: `curl -I http://localhost:8501`

---

**¡Tu aplicación PT_CALIDAD está lista para producción! 🎉**
