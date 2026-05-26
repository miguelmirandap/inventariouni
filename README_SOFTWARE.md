# Software de inventario (Python + SQLite)

Este proyecto tiene dos modos de uso:
- Consola (`app_inventario.py`)
- Web local (`app_web.py`)

## Archivos
- `app_inventario.py`: aplicacion de consola.
- `app_web.py`: interfaz web local con login y roles.
- `requirements.txt`: dependencias para modo web.
- `inventario.db`: base SQLite (se crea automaticamente).
- `INVENTARIO_BASE.csv`, `MOVIMIENTOS.csv`, `PROVEEDORES.csv`: datos iniciales.

## Funcionalidades implementadas
- Login por usuarios con roles:
  - `admin` puede registrar productos y movimientos.
  - `supervisor` gestiona ventas/cartera/reportes.
  - `caja` opera ventas y abonos.
- Dashboard con:
  - productos totales,
  - valor del inventario,
  - utilidad potencial,
  - contador de stock bajo.
- Modulo de productos con busqueda y estado de stock.
- Modulo de movimientos con validaciones de stock.
- Reportes por fecha y categoria:
  - resumen de ventas por categoria,
  - detalle de movimientos en rango.
- Modulo de cartera:
  - alta de clientes,
  - registro de deudas,
  - registro de abonos,
  - calculo de saldo pendiente por cliente y total.
- Modulo de ventas:
  - registro de venta de contado o fiado,
  - venta multi-producto en un solo ticket,
  - descuento automatico de stock,
  - registro automatico en movimientos (SALIDA),
  - creacion de deuda en cartera cuando la venta es fiada,
  - ticket imprimible por venta,
  - cierre diario de caja (contado/fiado, por usuario y top productos).
- Alertas inteligentes:
  - stock critico,
  - deudas vencidas con dias de atraso.
- Seguridad basica:
  - contrasenas con hash,
  - cambio de contrasena desde perfil.
- Respaldos:
  - respaldo automatico diario,
  - panel admin para crear/restaurar respaldos.
- Exportaciones:
  - CSV de inventario, ventas y cartera,
  - XLSX de ventas,
  - PDF de cierre diario.

## Ejecutar modo web
En PowerShell, dentro de esta carpeta:

```powershell
c:/python313/python.exe -m pip install -r requirements.txt
c:/python313/python.exe app_web.py
```

Abrir en navegador:

```text
http://127.0.0.1:5000
```

Usuarios iniciales:
- `admin / admin123`
- `supervisor / super123`
- `caja / caja123`

## Instalar para uso con doble clic (recomendado)
Este flujo crea un acceso directo en el escritorio para que solo abran el programa.

```powershell
powershell -ExecutionPolicy Bypass -File .\instalar_acceso_directo.ps1
```

Luego, abrir desde escritorio:
- `Inventario Cafeteria`

El acceso directo ejecuta `iniciar_inventario.bat`, inicia el servidor local y abre el navegador automaticamente.
El icono usado es `assets\icon_taza_check.ico` (taza + check).

## Opcional: generar un .exe
Si quieres empaquetar como ejecutable de Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\crear_exe.ps1
```

Salida esperada:
- `dist\InventarioCafeteria.exe`

## Icono del sistema
- `assets\icon_taza_check.ico`: icono de app para acceso directo y `.exe`.
- `assets\icon_taza_check.png`: vista previa del icono.

## Ejecutar modo consola
```powershell
c:/python313/python.exe app_inventario.py
```

## Recomendacion operativa
1. Usar modo web en el dia a dia (mas rapido para caja y admin).
2. Registrar todos los movimientos de venta/compra/ajuste.
3. Revisar `Reportes` al cierre diario o semanal.