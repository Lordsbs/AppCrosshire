# ⊕ Crosshair Overlay

Overlay de crosshair siempre encima de todas las ventanas, con configuración persistente.

## Requisitos

- Python 3.8 o superior
- Windows / Linux / macOS

## Instalación y uso

### Opción 1 – Automática (Windows)
Haz doble clic en `lanzar.bat`. Instala las dependencias y arranca la app.

### Opción 2 – Manual
```bash
pip install PyQt5
python crosshair.py
```

## Características

- **13 estilos de crosshair**: Cruz, X, Cruz+Círculo, Círculo, Francotirador, Chevron, Diamante, Cuadrado, Flecha, Estrella, Corchetes, Solo punto, Cruz corta
- **Punto central** activable independientemente
- **Modo T** (sin brazo derecho)
- **Colores** completamente personalizables con selector de color
- **Outline** configurable (color + grosor)
- **Tamaño, grosor y separación** con sliders en tiempo real
- **Relación de aspecto** para crosshairs más anchos o altos
- **Opacidad** ajustable
- **Config persistente** guardada automáticamente en `crosshair_config.json`
- **Icono en la bandeja del sistema** para acceso rápido
- **Preview en tiempo real** en la ventana de ajustes

## Configuración

La configuración se guarda en `crosshair_config.json` junto al script.
Al abrir la app se carga automáticamente.

## Atajos desde la bandeja del sistema

- **Doble clic** en el icono → abre la ventana de configuración
- **Clic derecho** → menú con opciones de mostrar/ocultar y salir
