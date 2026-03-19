# StyKMZ - Plugin para QGIS

**StyKMZ** es un plugin diseñado para optimizar la exportación de capas vectoriales desde QGIS hacia el formato KMZ (Google Earth). A diferencia de la exportación estándar, StyKMZ garantiza que se mantenga la integridad visual y estructural de los datos al consolidar múltiples capas.

## Características Principales

-   **Consolidación de Capas**: Agrupa múltiples capas de QGIS en un único archivo `.kmz` organizado por carpetas.
-   **Preservación de Estilos**: Cada capa mantiene su color original de QGIS gracias a un sistema de identificadores de estilo único que evita conflictos.
-   **Persistencia de Atributos**: Utiliza esquemas de datos únicos por capa (`KML Schemas`), lo que asegura que al re-importar el KMZ en QGIS, los campos de la tabla de atributos (columnas) se reconozcan e importen correctamente.
-   **Opacidad Forzada**: Ajusta automáticamente la opacidad de los colores al 100% para evitar elementos semitransparentes no deseados.
-   **Gestión de Etiquetas**: Permite seleccionar dinámicamente qué campo de la tabla de atributos se utilizará como nombre (`Name`) en el visor de Google Earth.

## Cómo Usar

1.  **Abrir el Plugin**: Haz clic en el icono de **StyKMZ** en la barra de herramientas de QGIS o búscalo en el menú `&StyKMZ`.
2.  **Seleccionar Capas**: En la lista de "Capas disponibles", selecciona las capas que deseas incluir en el archivo KMZ.
3.  **Configurar Nombre (Opcional)**: Elige el campo de la tabla de atributos que deseas usar como etiqueta principal para los elementos (`NameField`).
4.  **Definir Ruta de Salida**: Haz clic en el botón de selección de ruta para elegir dónde guardar tu archivo `.kmz`.
5.  **Exportar**: Presiona "Aceptar" para generar el archivo.

## Recomendaciones Técnicas

-   **Compatibilidad**: Diseñado para funcionar en entornos **QGIS 3.x**.

---
