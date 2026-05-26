# Inventario para tienda universitaria

## Archivos creados
- `INVENTARIO_BASE.csv`: catalogo principal de productos y stock actual.
- `MOVIMIENTOS.csv`: registro de entradas, salidas y ajustes.
- `PROVEEDORES.csv`: directorio de proveedores.

## Como usar (rapido)
1. Abre `INVENTARIO_BASE.csv` en Excel o Google Sheets.
2. Actualiza productos, costos, precios y stock minimo.
3. Cada venta/compra/ajuste registrala en `MOVIMIENTOS.csv`.
4. Al final del dia, actualiza `Stock_Actual` en `INVENTARIO_BASE.csv` segun movimientos.

## Regla clave de control
- Si `Stock_Actual <= Stock_Minimo`, el producto debe pasar a lista de reposicion.

## Columnas recomendadas para analisis en Excel
- `Valor_Stock` = `Stock_Actual * Precio_Compra`
- `Margen_Unitario` = `Precio_Venta - Precio_Compra`
- `Estado_Stock` = SI(Stock_Actual<=Stock_Minimo,"REABASTECER","OK")

## Sugerencia de rutina semanal
1. Revisar productos con estado `REABASTECER`.
2. Consolidar pedido por proveedor.
3. Verificar productos de alta rotacion (papeleria y snacks).
4. Hacer conteo fisico de una categoria por semana.

## Proximo paso opcional
Si quieres, puedo crearte una version automatizada en Excel (con hojas y formulas) o un sistema sencillo en Python para registrar ventas y actualizar stock automaticamente.