# ⊕ Crosshair Overlay

Overlay de crosshair siempre encima de todas las ventanas, con configuración persistente y sistema de perfiles.

## Uso rápido

### Opción 1 – Ejecutable portable (recomendado, sin instalación)

1. Ejecuta `build.bat` (Windows) o `./build.sh` (Linux/Mac)
2. El ejecutable se genera en `dist/CrosshairOverlay.exe`
3. Cópialo a cualquier carpeta y ejecútalo directamente

> La primera vez que se ejecute creará `crosshair_config.json` y `crosshair_profiles.json` en la misma carpeta.

### Opción 2 – Con Python

```bash
pip install PyQt5
python crosshair.py
```

## Estilos disponibles

| Estilo | Descripción |
|--------|-------------|
| Cruz clásica | La más universal |
| Solo punto | Máxima precisión, mínima distracción |
| Círculo | Ideal para armas de área |
| X (aspa) | Alternativa diagonal a la cruz |
| Círculo + Cruz | Estilo CS:GO |
| Corchetes | Estilo táctico/competitivo |
| Punto + Círculo | Punto central dentro de círculo, ideal para sniper |

## Características

- **Modo T** elimina el brazo superior para formar una T
- **Punto central** activable en cualquier estilo
- **Colores** completamente personalizables (principal + outline)
- **Outline** configurable: color independiente y grosor
- **Tamaño, grosor y separación** con sliders en tiempo real
- **Relación de aspecto** para crosshairs más anchos o altos
- **Opacidad** ajustable (solo afecta al color principal, el outline siempre opaco)
- **Multi-monitor**: selector de pantalla con detección automática
- **Perfiles**: guarda, carga, crea y elimina configuraciones guardadas
- **Preview en tiempo real** en la ventana de ajustes
- **Config persistente** guardada automáticamente al cerrar

## Perfiles

- **Cargar** – aplica la configuración del perfil seleccionado
- **Guardar aquí** – sobreescribe el perfil seleccionado con la config actual
- **Nuevo perfil** – crea un perfil con la config actual
- **Eliminar** – borra el perfil; si era el activo, carga el siguiente automáticamente

## Bandeja del sistema

- **Doble clic** en el icono → abre la ventana de configuración
- **Clic derecho** → menú con opciones de mostrar/ocultar y salir
