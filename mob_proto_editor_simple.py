#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metin2 Mob Proto Editor - Simple Version
Optimized for fast loading and performance
"""

import sys
import os
import shutil
from datetime import datetime

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("PyQt5 not found. Please install it: pip install PyQt5")
    sys.exit(1)

class SimpleMobEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.data = []
        self.headers = []
        self.mob_names = {}  # VNUM -> Name lookup table
        
        self.init_ui()
        self.setWindowTitle("Metin2 Mob Proto Editor - Simple")
        self.setGeometry(100, 100, 1200, 600)
        
        # Try to load mob names lookup table
        self.load_mob_names()
        
    def init_ui(self):
        # Create menu bar
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu('Edit')
        
        mass_edit_action = QAction('Mass Edit...', self)
        mass_edit_action.setShortcut('Ctrl+M')
        mass_edit_action.triggered.connect(self.show_mass_edit)
        edit_menu.addAction(mass_edit_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu('Tools')
        
        fix_names_action = QAction('Fix mob_names.txt Encoding', self)
        fix_names_action.triggered.connect(self.fix_mob_names_file)
        tools_menu.addAction(fix_names_action)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Simple toolbar
        toolbar_layout = QHBoxLayout()
        
        open_btn = QPushButton('Open File')
        open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_btn)
        
        save_btn = QPushButton('Save File')
        save_btn.clicked.connect(self.save_file)
        toolbar_layout.addWidget(save_btn)
        
        mass_edit_btn = QPushButton('Mass Edit')
        mass_edit_btn.clicked.connect(self.show_mass_edit)
        toolbar_layout.addWidget(mass_edit_btn)
        
        fix_names_btn = QPushButton('Fix Names File')
        fix_names_btn.clicked.connect(self.fix_mob_names_file)
        toolbar_layout.addWidget(fix_names_btn)
        
        toolbar_layout.addStretch()
        
        # Search box
        search_label = QLabel('Search:')
        toolbar_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search mobs...')
        self.search_box.textChanged.connect(self.filter_data)
        toolbar_layout.addWidget(self.search_box)
        
        layout.addLayout(toolbar_layout)
        
        # Table widget with minimal features
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Set font that can display Korean/Asian characters
        font = QFont()
        font.setFamily("Arial Unicode MS, Malgun Gothic, Microsoft YaHei, SimSun")
        font.setPointSize(9)
        self.table.setFont(font)
        
        layout.addWidget(self.table)
        
        # Status
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready - Click Open File to load mob_proto.txt')
        
    def open_file(self):
        default_path = os.path.join(os.path.dirname(__file__), 'mob_proto.txt')
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open mob_proto.txt', default_path, 'Text files (*.txt)')
            
        if file_path:
            self.load_file_fast(file_path)
            
    def load_file_fast(self, file_path):
        """Fast loading without fancy progress bars"""
        try:
            self.status_bar.showMessage('Loading file...')
            QApplication.processEvents()
            
            # Try different encodings to properly display Korean/Asian characters
            lines = None
            encodings_to_try = ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]
                    self.file_encoding = encoding  # Store successful encoding
                    self.status_bar.showMessage(f'Loaded with {encoding} encoding')  
                    break
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
                    
            if lines is None:
                # Fallback: read as binary and decode with error handling
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
            if not lines:
                QMessageBox.warning(self, 'Warning', 'File is empty')
                return
                
            # Parse quickly
            self.headers = lines[0].split('\t')
            self.data = []
            
            for line in lines[1:]:
                row = line.split('\t')
                # Pad row to match headers
                while len(row) < len(self.headers):
                    row.append('')
                self.data.append(row)
                
            self.file_path = file_path
            self.setup_table()
            
            self.status_bar.showMessage(f'Loaded {len(self.data)} mobs from {os.path.basename(file_path)}')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load file: {str(e)}')
            
    def setup_table(self):
        """Setup table without expensive operations"""
        # Basic table setup
        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        
        # Fill table data with name lookup and replacement
        for row, row_data in enumerate(self.data):
            for col, value in enumerate(row_data):
                # Special handling for NAME column (usually column 1)
                if col == 1 and self.headers[col] == 'NAME':
                    vnum = row_data[0] if len(row_data) > 0 else ''
                    german_name = self.get_mob_name(vnum, value)
                    # Replace the actual data with German name
                    self.data[row][col] = german_name  
                    item = QTableWidgetItem(str(german_name))
                else:
                    item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
                
        # Set column widths manually for important columns
        important_cols = ['VNUM', 'NAME', 'LEVEL', 'TYPE', 'EXP', 'GOLD_MIN', 'GOLD_MAX']
        for i, header in enumerate(self.headers):
            if header in important_cols and i < 10:  # Only first 10 columns
                self.table.resizeColumnToContents(i)
            else:
                self.table.setColumnWidth(i, 80)  # Fixed width for others
                
    def filter_data(self):
        """Simple text filter"""
        search_text = self.search_box.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            if search_text:
                # Check VNUM and NAME columns only for speed
                vnum_item = self.table.item(row, 0)  # VNUM
                name_item = self.table.item(row, 1)  # NAME
                
                vnum_text = vnum_item.text().lower() if vnum_item else ''
                name_text = name_item.text().lower() if name_item else ''
                
                show_row = search_text in vnum_text or search_text in name_text
                
            self.table.setRowHidden(row, not show_row)
            
    def save_file(self):
        if not self.file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Save mob_proto.txt', 'mob_proto.txt', 'Text files (*.txt)')
        else:
            file_path = self.file_path
            
        if file_path:
            self.save_to_file(file_path)
            
    def save_to_file(self, file_path):
        try:
            # Create backup
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(file_path, backup_path)
                
            # Collect current data from table (including German names)
            current_data = []
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                current_data.append(row_data)
                
            # Write file with UTF-8 encoding to support German characters
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\t'.join(self.headers) + '\n')
                for row_data in current_data:
                    f.write('\t'.join(row_data) + '\n')
                    
            self.status_bar.showMessage(f'Saved to {os.path.basename(file_path)}')
            QMessageBox.information(self, 'Success', 'File saved successfully!')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save file: {str(e)}')
            
    def load_mob_names(self):
        """Load mob names from mob_names.txt for proper name display"""
        names_file = os.path.join(os.path.dirname(__file__), 'mob_names.txt')
        
        if not os.path.exists(names_file):
            return
            
        try:
            # Try different encodings for mob_names.txt
            encodings_to_try = ['cp1252', 'iso-8859-1', 'utf-8', 'cp949', 'latin1']
            
            for encoding in encodings_to_try:
                try:
                    with open(names_file, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    
                    # Parse VNUM -> Name mapping
                    for line in lines[1:]:  # Skip header
                        if line.strip() and '\t' in line:
                            parts = line.strip().split('\t')
                            if len(parts) >= 2:
                                vnum = parts[0].strip()
                                name = parts[1].strip()
                                
                                # Fix common encoding issues for German characters
                                name = name.replace('�', 'ä').replace('�', 'ö').replace('�', 'ü')
                                name = name.replace('�', 'Ä').replace('�', 'Ö').replace('�', 'Ü')
                                name = name.replace('�', 'ß').replace('�', 'é').replace('�', 'è')
                                name = name.replace('k�mpfer', 'kämpfer').replace('anf�hrer', 'anführer')
                                name = name.replace('B�ser', 'Böser').replace('f�r', 'für')
                                
                                self.mob_names[vnum] = name
                    
                    if self.mob_names:
                        self.status_bar.showMessage(f'Loaded {len(self.mob_names)} mob names from mob_names.txt')
                        break
                        
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Could not load mob_names.txt: {e}")
            
    def get_mob_name(self, vnum, original_name):
        """Get proper mob name from lookup table, fallback to original"""
        if str(vnum) in self.mob_names:
            return self.mob_names[str(vnum)]
        elif original_name and original_name not in ['??', '???', '????']:
            return original_name
        else:
            return f"Mob {vnum}"
            
    def fix_mob_names_file(self):
        """Fix encoding issues in mob_names.txt file"""
        names_file = os.path.join(os.path.dirname(__file__), 'mob_names.txt')
        
        if not os.path.exists(names_file):
            QMessageBox.warning(self, 'Warning', 'mob_names.txt not found')
            return
            
        try:
            # Create backup first
            backup_path = f"{names_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(names_file, backup_path)
            
            # Read original file with different encodings
            lines = None
            original_encoding = None
            encodings_to_try = ['cp1252', 'iso-8859-1', 'utf-8', 'cp949', 'latin1']
            
            for encoding in encodings_to_try:
                try:
                    with open(names_file, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    original_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
                    
            if lines is None:
                QMessageBox.critical(self, 'Error', 'Could not read mob_names.txt with any encoding')
                return
                
            # Fix encoding issues
            fixed_lines = []
            changes_made = 0
            
            for line in lines:
                original_line = line
                fixed_line = line
                
                # Apply all encoding fixes
                fixed_line = fixed_line.replace('�', 'ä').replace('�', 'ö').replace('�', 'ü')
                fixed_line = fixed_line.replace('�', 'Ä').replace('�', 'Ö').replace('�', 'Ü')
                fixed_line = fixed_line.replace('�', 'ß').replace('�', 'é').replace('�', 'è')
                fixed_line = fixed_line.replace('k�mpfer', 'kämpfer').replace('anf�hrer', 'anführer')
                fixed_line = fixed_line.replace('B�ser', 'Böser').replace('f�r', 'für')
                
                # Additional common fixes
                fixed_line = fixed_line.replace('�ber', 'über').replace('gr��er', 'größer')
                fixed_line = fixed_line.replace('w�tend', 'wütend').replace('sch�n', 'schön')
                
                if fixed_line != original_line:
                    changes_made += 1
                    
                fixed_lines.append(fixed_line)
                
            # Write fixed file as UTF-8
            with open(names_file, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
                
            # Reload mob names
            self.mob_names.clear()
            self.load_mob_names()
            
            # Update table if data is loaded
            if self.data:
                self.setup_table()
                
            QMessageBox.information(
                self, 'Success', 
                f'Fixed {changes_made} encoding issues in mob_names.txt\n'
                f'Backup created: {os.path.basename(backup_path)}\n'
                f'File saved as UTF-8 encoding'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to fix mob_names.txt: {str(e)}')
            
    def show_mass_edit(self):
        """Show mass edit dialog for bulk changes"""
        if not self.data:
            QMessageBox.warning(self, 'Warning', 'No data loaded')
            return
            
        dialog = MassEditDialog(self.headers, self)
        if dialog.exec_() == QDialog.Accepted:
            changes = dialog.get_changes()
            self.apply_mass_changes(changes)
            
    def apply_mass_changes(self, changes):
        """Apply mass changes to the data"""
        if not changes:
            return
            
        # Get selected rows or use all rows
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
            
        rows_to_change = list(selected_rows) if selected_rows else list(range(self.table.rowCount()))
        
        changes_made = 0
        
        for row in rows_to_change:
            for col_name, operation, value in changes:
                # Find column index
                col_index = -1
                for i, header in enumerate(self.headers):
                    if header == col_name:
                        col_index = i
                        break
                        
                if col_index >= 0:
                    try:
                        item = self.table.item(row, col_index)
                        current_val = float(item.text()) if item and item.text() else 0
                        
                        if operation == 'multiply':
                            new_val = current_val * float(value)
                        elif operation == 'add':
                            new_val = current_val + float(value)
                        elif operation == 'set':
                            new_val = float(value)
                        else:
                            continue
                            
                        # Update table item
                        new_item = QTableWidgetItem(str(int(new_val)))
                        self.table.setItem(row, col_index, new_item)
                        changes_made += 1
                        
                    except (ValueError, TypeError):
                        continue
                        
        if changes_made > 0:
            self.status_bar.showMessage(f'Applied {changes_made} changes to selected mobs')
            QMessageBox.information(self, 'Success', f'Applied {changes_made} changes successfully!')
        else:
            QMessageBox.warning(self, 'Warning', 'No changes were applied')


class MassEditDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.changes = []
        
        self.setWindowTitle('Mass Edit - Bulk Changes')
        self.setModal(True)
        self.resize(500, 400)
        
        # Set font for Korean/Asian characters
        font = QFont()
        font.setFamily("Arial Unicode MS, Malgun Gothic, Microsoft YaHei, SimSun")
        font.setPointSize(9)
        self.setFont(font)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel('Select columns to modify and specify operations.\nChanges apply to selected rows, or all rows if none selected.')
        info_label.setWordWrap(True)
        info_label.setFont(self.font())  # Apply Unicode font
        layout.addWidget(info_label)
        
        # Scroll area for operations
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setFont(self.font())  # Apply Unicode font to scroll widget
        self.scroll_layout = QVBoxLayout(scroll_widget)
        
        # Common numeric columns for mass editing
        common_columns = [
            ('EXP', 'Experience points'),
            ('GOLD_MIN', 'Minimum gold drop'),
            ('GOLD_MAX', 'Maximum gold drop'),
            ('LEVEL', 'Mob level'),
            ('MAX_HP', 'Health points'),
            ('DAMAGE_MIN', 'Minimum damage'),
            ('DAMAGE_MAX', 'Maximum damage'),
            ('DEF', 'Defense'),
            ('ATTACK_SPEED', 'Attack speed'),
            ('MOVE_SPEED', 'Movement speed'),
            ('ST', 'Strength'),
            ('DX', 'Dexterity'),
            ('HT', 'Health'),
            ('IQ', 'Intelligence')
        ]
        
        self.operation_widgets = []
        
        for col_name, description in common_columns:
            if col_name in self.headers:
                group = QGroupBox(f"{col_name} - {description}")
                group.setFont(self.font())  # Apply Unicode font to group
                group_layout = QGridLayout(group)
                
                enable_cb = QCheckBox('Enable')
                enable_cb.setFont(self.font())  # Apply Unicode font
                operation_combo = QComboBox()
                operation_combo.setFont(self.font())  # Apply Unicode font
                operation_combo.addItems(['multiply', 'set', 'add'])
                value_edit = QLineEdit()
                value_edit.setFont(self.font())  # Apply Unicode font
                value_edit.setPlaceholderText('Value (e.g., 4 for x4, 300 for set)')
                
                # Add some quick preset buttons for common operations
                preset_layout = QHBoxLayout()
                if col_name == 'EXP':
                    x2_btn = QPushButton('x2')
                    x4_btn = QPushButton('x4')
                    x2_btn.clicked.connect(lambda _, v=value_edit, o=operation_combo: self.set_preset(v, o, '2', 'multiply'))
                    x4_btn.clicked.connect(lambda _, v=value_edit, o=operation_combo: self.set_preset(v, o, '4', 'multiply'))
                    preset_layout.addWidget(x2_btn)
                    preset_layout.addWidget(x4_btn)
                elif col_name in ['GOLD_MIN', 'GOLD_MAX']:
                    btn_300 = QPushButton('300')
                    btn_600 = QPushButton('600')
                    btn_300.clicked.connect(lambda _, v=value_edit, o=operation_combo: self.set_preset(v, o, '300', 'set'))
                    btn_600.clicked.connect(lambda _, v=value_edit, o=operation_combo: self.set_preset(v, o, '600', 'set'))
                    preset_layout.addWidget(btn_300)
                    preset_layout.addWidget(btn_600)
                
                group_layout.addWidget(enable_cb, 0, 0)
                group_layout.addWidget(operation_combo, 0, 1)
                group_layout.addWidget(value_edit, 0, 2)
                group_layout.addLayout(preset_layout, 1, 0, 1, 3)
                
                self.scroll_layout.addWidget(group)
                self.operation_widgets.append((col_name, enable_cb, operation_combo, value_edit))
                
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton('Apply Changes')
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
    def set_preset(self, value_edit, operation_combo, value, operation):
        """Set preset values for quick access"""
        value_edit.setText(value)
        operation_combo.setCurrentText(operation)
        
    def get_changes(self):
        """Get all enabled changes"""
        changes = []
        
        for col_name, enable_cb, operation_combo, value_edit in self.operation_widgets:
            if enable_cb.isChecked() and value_edit.text():
                try:
                    float(value_edit.text())  # Validate numeric
                    changes.append((col_name, operation_combo.currentText(), value_edit.text()))
                except ValueError:
                    continue
                    
        return changes


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Metin2 Mob Proto Editor Simple')
    
    window = SimpleMobEditor()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
