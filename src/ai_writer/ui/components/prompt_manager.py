"""Prompt management dialog for AI Writer."""

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from ai_writer.core import get_prompt_manager
from ai_writer.config.settings import Prompt


class PromptManagerDialog(QDialog):
    """Dialog for managing prompt templates."""
    
    def __init__(self, parent=None):
        """Initialize the prompt manager dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.prompt_manager = get_prompt_manager()
        self.current_prompt = None
        self._setup_ui()
        self._connect_signals()
        self.refresh_prompt_list()
        self.setModal(True)
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Manage Prompt Templates")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - prompt list
        left_panel = self._create_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - prompt editor
        right_panel = self._create_editor_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([250, 450])
        layout.addWidget(splitter)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_list_panel(self) -> QWidget:
        """Create the prompt list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Prompt Templates")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # List widget
        self.prompt_list = QListWidget()
        self.prompt_list.setMinimumWidth(200)
        layout.addWidget(self.prompt_list)
        
        # List control buttons
        list_buttons = QHBoxLayout()
        
        self.new_btn = QPushButton("New")
        self.new_btn.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        list_buttons.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.delete_btn.setEnabled(False)
        list_buttons.addWidget(self.delete_btn)
        
        layout.addLayout(list_buttons)
        
        return panel
    
    def _create_editor_panel(self) -> QWidget:
        """Create the prompt editor panel.""" 
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Prompt Editor")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter prompt name...")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Model field
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["all", "llama2", "codellama", "mistral", "neural-chat"])
        self.model_combo.setEditable(True)
        self.model_combo.setToolTip("Target language model ('all' for any model)")
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Description field
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Optional description...")
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # Content field
        layout.addWidget(QLabel("Prompt Content:"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Enter your prompt template here...\\n\\nTip: The text to be continued will be appended to this prompt.")
        self.content_edit.setMinimumHeight(200)
        layout.addWidget(self.content_edit)
        
        # Editor control buttons
        editor_buttons = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setIcon(self.style().standardIcon(self.style().SP_DialogSaveButton))
        self.save_btn.setEnabled(False)
        editor_buttons.addWidget(self.save_btn)
        
        self.revert_btn = QPushButton("Revert")
        self.revert_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        self.revert_btn.setEnabled(False)
        editor_buttons.addWidget(self.revert_btn)
        
        editor_buttons.addStretch()
        layout.addLayout(editor_buttons)
        
        return panel
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.prompt_list.currentRowChanged.connect(self._on_prompt_selected)
        self.new_btn.clicked.connect(self._create_new_prompt)
        self.delete_btn.clicked.connect(self._delete_prompt)
        self.save_btn.clicked.connect(self._save_prompt)
        self.revert_btn.clicked.connect(self._revert_changes)
        
        # Enable save/revert buttons when content changes
        self.name_edit.textChanged.connect(self._on_content_changed)
        self.desc_edit.textChanged.connect(self._on_content_changed)
        self.content_edit.textChanged.connect(self._on_content_changed)
        self.model_combo.currentTextChanged.connect(self._on_content_changed)
    
    def refresh_prompt_list(self):
        """Refresh the prompt list."""
        self.prompt_list.clear()
        
        prompts = self.prompt_manager.get_all_prompts()
        for prompt in prompts:
            item = QListWidgetItem(prompt.name)
            item.setData(Qt.UserRole, prompt.id)
            item.setToolTip(f"Model: {prompt.language_model}\\n{prompt.description}")
            self.prompt_list.addItem(item)
        
        if prompts:
            self.prompt_list.setCurrentRow(0)
    
    def _on_prompt_selected(self, row: int):
        """Handle prompt selection from list.
        
        Args:
            row: Selected row index
        """
        if row < 0:
            self.current_prompt = None
            self._clear_editor()
            return
            
        item = self.prompt_list.item(row)
        prompt_id = item.data(Qt.UserRole)
        prompt = self.prompt_manager.get_prompt(prompt_id)
        
        if prompt:
            self.current_prompt = prompt
            self._load_prompt_to_editor(prompt)
            self.delete_btn.setEnabled(True)
        else:
            self.current_prompt = None
            self._clear_editor()
    
    def _load_prompt_to_editor(self, prompt: Prompt):
        """Load a prompt into the editor fields.
        
        Args:
            prompt: Prompt to load
        """
        # Block signals to avoid triggering change detection
        self.name_edit.blockSignals(True)
        self.desc_edit.blockSignals(True)
        self.content_edit.blockSignals(True)
        self.model_combo.blockSignals(True)
        
        try:
            self.name_edit.setText(prompt.name)
            self.desc_edit.setText(prompt.description)
            self.content_edit.setPlainText(prompt.content)
            
            # Set model combo
            index = self.model_combo.findText(prompt.language_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            else:
                self.model_combo.setCurrentText(prompt.language_model)
        finally:
            # Restore signals
            self.name_edit.blockSignals(False)
            self.desc_edit.blockSignals(False)
            self.content_edit.blockSignals(False)
            self.model_combo.blockSignals(False)
        
        # Reset change tracking
        self.save_btn.setEnabled(False)
        self.revert_btn.setEnabled(False)
    
    def _clear_editor(self):
        """Clear the editor fields."""
        self.name_edit.clear()
        self.desc_edit.clear()
        self.content_edit.clear()
        self.model_combo.setCurrentIndex(0)
        self.save_btn.setEnabled(False)
        self.revert_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    def _create_new_prompt(self):
        """Create a new prompt."""
        # Create a new prompt with default values
        new_prompt = self.prompt_manager.create_prompt(
            name="New Prompt",
            content="",
            language_model="all",
            description=""
        )
        
        # Refresh list and select the new prompt
        self.refresh_prompt_list()
        
        # Find and select the new prompt
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            if item.data(Qt.UserRole) == new_prompt.id:
                self.prompt_list.setCurrentRow(i)
                break
        
        # Focus name field for editing
        self.name_edit.selectAll()
        self.name_edit.setFocus()
    
    def _delete_prompt(self):
        """Delete the current prompt."""
        if not self.current_prompt:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Prompt",
            f"Are you sure you want to delete the prompt '{self.current_prompt.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.prompt_manager.delete_prompt(self.current_prompt.id)
            self.refresh_prompt_list()
    
    def _save_prompt(self):
        """Save the current prompt."""
        if not self.current_prompt:
            return
            
        # Validate input
        name = self.name_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Prompt name cannot be empty.")
            return
            
        if not content:
            QMessageBox.warning(self, "Invalid Input", "Prompt content cannot be empty.")
            return
        
        # Update the prompt
        success = self.prompt_manager.update_prompt(
            self.current_prompt.id,
            name=name,
            content=content,
            language_model=self.model_combo.currentText(),
            description=self.desc_edit.text().strip()
        )
        
        if success:
            # Refresh the list to show updated name
            self.refresh_prompt_list()
            
            # Find and reselect the updated prompt
            for i in range(self.prompt_list.count()):
                item = self.prompt_list.item(i)
                if item.data(Qt.UserRole) == self.current_prompt.id:
                    self.prompt_list.setCurrentRow(i)
                    break
            
            # Reset change tracking
            self.save_btn.setEnabled(False)
            self.revert_btn.setEnabled(False)
    
    def _revert_changes(self):
        """Revert editor to the current prompt state."""
        if self.current_prompt:
            self._load_prompt_to_editor(self.current_prompt)
    
    def _on_content_changed(self):
        """Handle content change in editor."""
        if self.current_prompt:
            self.save_btn.setEnabled(True)
            self.revert_btn.setEnabled(True)