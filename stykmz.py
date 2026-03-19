# -*- coding: utf-8 -*-
import os
import tempfile
import zipfile
import shutil
import re
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import (
    QgsVectorFileWriter,
    QgsProject,
    QgsMapLayerType
)

from .stykmz_dialog import StyKMZDialog

class StyKMZ:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = u'&StyKMZ'
        self.first_start = None

    def add_action(self, icon_path, text, callback, enabled_flag=True, 
                   add_to_menu=True, add_to_toolbar=True, 
                   status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip: action.setStatusTip(status_tip)
        if whats_this: action.setWhatsThis(whats_this)
        if add_to_toolbar: self.iface.addToolBarIcon(action)
        if add_to_menu: self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(icon_path, text=u'Exportar a KMZ (StyKMZ)', callback=self.run, parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(u'&StyKMZ', action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.first_start:
            self.first_start = False
            self.dlg = StyKMZDialog()
            self.dlg.pushButtonRuta.clicked.connect(self.select_output_file)
            self.dlg.listWidgetCapas.itemSelectionChanged.connect(self.update_fields)
            
        self.dlg.listWidgetCapas.clear()
        if hasattr(self.dlg, 'comboBoxNombre'):
            self.dlg.comboBoxNombre.clear()
        
        layers = QgsProject.instance().mapLayers().values()
        self.vector_layers = []
        for layer in layers:
            if layer.type() == QgsMapLayerType.VectorLayer:
                self.dlg.listWidgetCapas.addItem(layer.name())
                self.vector_layers.append(layer)
                
        self.dlg.show()
        result = self.dlg.exec_()
        
        if result:
            selected_items = self.dlg.listWidgetCapas.selectedItems()
            if not selected_items:
                QMessageBox.warning(self.iface.mainWindow(), u"Atención", "Seleccione al menos una capa.")
                return
                
            selected_layer_names = [item.text() for item in selected_items]
            layers_to_export = [l for l in self.vector_layers if l.name() in selected_layer_names]
            output_kmz_path = self.dlg.lineEditRuta.text()
            
            name_field = ""
            if hasattr(self.dlg, 'comboBoxNombre'):
                name_field = self.dlg.comboBoxNombre.currentText()
            
            if not output_kmz_path:
                QMessageBox.warning(self.iface.mainWindow(), u"Atención", "Especifique la ruta de salida.")
                return
                
            self.exportar_capas_a_kmz(layers_to_export, output_kmz_path, name_field)

    def update_fields(self):
        if not hasattr(self.dlg, 'comboBoxNombre'):
            return
        self.dlg.comboBoxNombre.clear()
        selected_items = self.dlg.listWidgetCapas.selectedItems()
        if not selected_items: return
            
        layer_name = selected_items[0].text()
        layer = next((l for l in self.vector_layers if l.name() == layer_name), None)
        if layer:
            fields = [field.name() for field in layer.fields()]
            comunes = ['Name', 'Nombre', 'id', 'fid', 'Oid', 'Desc']
            todos = list(dict.fromkeys(comunes + fields))
            self.dlg.comboBoxNombre.addItems(todos)

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self.dlg, "Guardar KMZ", "", "KMZ Files (*.kmz)")
        if file_path:
            self.dlg.lineEditRuta.setText(file_path)

    def exportar_capas_a_kmz(self, layers, output_kmz_path, name_field=""):
        temp_dir = tempfile.mkdtemp()
        kml_files = []
        try:
            for idx, layer in enumerate(layers):
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.driverName = "KML"
                # Activamos FeatureSymbology para que cada capa mantenga su color/estilo y se puedan diferenciar.
                # NOTA: Al abrirlo en QGIS se cargará como 'Símbolos Incorporados', que es necesario para mantener colores separados por KMZ.
                options.symbologyExport = QgsVectorFileWriter.FeatureSymbology 
                options.layerName = layer.name() # Agrupa la capa en un <Folder> dentro del KML individual
                
                if name_field:
                    options.layerOptions = [f"NameField={name_field}", "EXTENDED_DATA=YES"]
                else:
                    options.layerOptions = ["EXTENDED_DATA=YES"]
                
                options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
                
                transform_context = QgsProject.instance().transformContext()
                
                safe_name = f"layer_{idx}.kml"
                layer_kml_path = os.path.join(temp_dir, safe_name)
                
                res = QgsVectorFileWriter.writeAsVectorFormatV3(layer, layer_kml_path, transform_context, options)
                
                if isinstance(res, tuple):
                    error = res[0]
                    error_msg = res[1] if len(res) > 1 else "Error desconocido"
                else:
                    error = res
                    error_msg = "Error desconocido"
                
                if error == QgsVectorFileWriter.NoError:
                    kml_files.append(layer_kml_path)
                else:
                    self.iface.messageBar().pushMessage("Error", f"Error exportando capa {layer.name()}: {error_msg}")
            
            if kml_files:
                doc_kml_path = os.path.join(temp_dir, "doc.kml")
                kmz_name = os.path.splitext(os.path.basename(output_kmz_path))[0]
                
                with open(doc_kml_path, 'w', encoding='utf-8') as doc_f:
                    doc_f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
                    doc_f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
                    doc_f.write('<Document id="root_doc">\n')
                    doc_f.write(f'  <name>{kmz_name}</name>\n')
                    
                    for idx_kml, kml_file in enumerate(kml_files):
                        with open(kml_file, 'r', encoding='utf-8') as in_f:
                            content = in_f.read()
                        
                        # Evitar colisión de estilos (IDs) entre diferentes capas para que mantengan sus colores individuales
                        content = re.sub(r'<(Style|StyleMap)([^>]*)id="([^"]+)"', rf'<\1\2id="\3_{idx_kml}"', content)
                        content = re.sub(r'<styleUrl>#([^<]+)</styleUrl>', rf'<styleUrl>#\1_{idx_kml}</styleUrl>', content)
                        
                        # Evitar colisión de Schemas para que QGIS reconozca los campos de atributos por separado
                        content = re.sub(r'<Schema([^>]*)id="([^"]+)"', rf'<Schema\1id="\2_{idx_kml}"', content)
                        content = re.sub(r'<SchemaData schemaUrl="#([^"]+)">', rf'<SchemaData schemaUrl="#\1_{idx_kml}">', content)
                        
                        # TOQUE FINAL: Forzar opacidad al 100% (Alpha = ff) en todos los colores
                        content = re.sub(r'<color>[0-9a-fA-F]{2}([0-9a-fA-F]{6})</color>', r'<color>ff\1</color>', content)
                        
                        # Extraer todo el contenido dentro de <Document> (Schemas, Folders, Placemarks)
                        match = re.search(r'<Document[^>]*>(.*?)</Document>', content, re.DOTALL)
                        if match:
                            doc_f.write(match.group(1) + '\n')
                            
                    doc_f.write('</Document>\n')
                    doc_f.write('</kml>\n')
                
                # Empaquetar el único doc.kml consolidado dentro del KMZ final
                with zipfile.ZipFile(output_kmz_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
                    kmz.write(doc_kml_path, "doc.kml")
                self.iface.messageBar().pushMessage(u"Éxito", f"KMZ creado exitosamente con {len(kml_files)} capas en carpetas conjuntas.", level=0, duration=5)
            else:
                self.iface.messageBar().pushMessage(u"Atención", u"No se generó ningún KML.", level=1, duration=5)
                
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
