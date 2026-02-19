"""Prompt selector component for AI Writer."""

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ai_writer.core import get_prompt_manager


class PromptSelector(QWidget):
    """Widget for selecting and managing prompts."""
    
    prompt_changed = pyqtSignal(str)  # Emitted when prompt selection changes
    
    def __init__(self, parent=None):
        """Initialize the prompt selector.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.prompt_manager = get_prompt_manager()
        self.current_model = "all"  # Track current model for filtering
        self._setup_ui()
        self._connect_signals()
        self.refresh_prompts()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Dropdown for prompt selection
        self.prompt_combo = QComboBox()
        self.prompt_combo.setMinimumWidth(140)
        self.prompt_combo.setToolTip("Select a prompt template")
        layout.addWidget(self.prompt_combo)
        
        # Manage prompts button
        self.manage_btn = QPushButton("⚙️")
        self.manage_btn.setFixedSize(QSize(24, 24))
        self.manage_btn.setToolTip("Manage prompt templates")
        layout.addWidget(self.manage_btn)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.prompt_combo.currentIndexChanged.connect(self._on_prompt_selection_changed)
        self.manage_btn.clicked.connect(self._open_prompt_manager)
    
    def refresh_prompts(self):
        """Refresh the prompt list for the current model."""
        current_selection = self.get_selected_prompt_id()
        
        # Clear combo box
        self.prompt_combo.clear()
        
        # Add "None" option
        self.prompt_combo.addItem("No prompt", None)
        
        # Add prompts for current model
        prompts = self.prompt_manager.get_prompts_for_model(self.current_model)
        for prompt in prompts:
            self.prompt_combo.addItem(f"{prompt.name}", prompt.id)
        
        # Restore selection if possible
        if current_selection:
            index = self.prompt_combo.findData(current_selection)
            if index >= 0:
                self.prompt_combo.setCurrentIndex(index)
        
        self._update_preview()
    
    def set_model_filter(self, model: str):
        """Set the current model for filtering prompts.
        
        Args:
            model: Model name to filter by
        """
        if model != self.current_model:
            self.current_model = model
            self.refresh_prompts()
    
    def get_selected_prompt_id(self) -> str | None:
        """Get the ID of the currently selected prompt.
        
        Returns:
            Prompt ID or None if no prompt selected
        """
        current_data = self.prompt_combo.currentData()
        return current_data if current_data else None
    
    def set_selected_prompt_id(self, prompt_id: str | None):
        """Set the selected prompt by ID.
        
        Args:
            prompt_id: ID of prompt to select, or None for no selection
        """
        if prompt_id is None:
            self.prompt_combo.setCurrentIndex(0)  # "No prompt" option
        else:
            index = self.prompt_combo.findData(prompt_id)
            if index >= 0:
                self.prompt_combo.setCurrentIndex(index)
    
    def get_selected_prompt_content(self) -> str | None:
        """Get the content of the currently selected prompt.
        
        Returns:
            Prompt content or None if no prompt selected
        """
        prompt_id = self.get_selected_prompt_id()
        if not prompt_id:
            return None
            
        prompt = self.prompt_manager.get_prompt(prompt_id)
        return prompt.content if prompt else None
    
    def _on_prompt_selection_changed(self):
        """Handle prompt selection change."""
        prompt_id = self.get_selected_prompt_id()
        
        # Update settings
        self.prompt_manager.set_selected_prompt(prompt_id)
        
        # Update preview
        self._update_preview()
        
        # Emit signal
        content = self.get_selected_prompt_content() or ""
        self.prompt_changed.emit(content)
    
    def _update_preview(self):
        """Update the prompt tooltip with preview."""
        content = self.get_selected_prompt_content()
        if not content:
            self.prompt_combo.setToolTip("No prompt selected")
        else:
            preview = content.strip()
            if len(preview) > 100:
                preview = preview[:97] + "..."
            self.prompt_combo.setToolTip(preview)
    
    def _open_prompt_manager(self):
        """Open the prompt management dialog."""
        from ai_writer.ui.components.prompt_manager import PromptManagerDialog
        
        dialog = PromptManagerDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Refresh prompts after dialog closes
            self.refresh_prompts()