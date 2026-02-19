"""Prompt management for AI Writer.

This module provides high-level functions for managing prompt templates,
including CRUD operations and filtering by language model.
"""

from typing import List, Optional

from ai_writer.config import get_settings, save_settings
from ai_writer.config.settings import Prompt


class PromptManager:
    """Manager for prompt templates with high-level operations."""
    
    def __init__(self):
        """Initialize the prompt manager."""
        self.settings = get_settings()
    
    def create_prompt(
        self, 
        name: str, 
        content: str, 
        language_model: str = "all", 
        description: str = ""
    ) -> Prompt:
        """Create a new prompt and save it to settings.
        
        Args:
            name: Display name for the prompt
            content: The prompt template content
            language_model: Target model name or "all"
            description: Optional description
            
        Returns:
            The created Prompt object
        """
        prompt = Prompt.create(name, content, language_model, description)
        self.settings.prompts.add_prompt(prompt)
        save_settings()
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by ID.
        
        Args:
            prompt_id: ID of the prompt to retrieve
            
        Returns:
            Prompt object if found, None otherwise
        """
        return self.settings.prompts.get_prompt(prompt_id)
    
    def get_all_prompts(self) -> List[Prompt]:
        """Get all stored prompts.
        
        Returns:
            List of all prompts
        """
        return self.settings.prompts.prompts
    
    def get_prompts_for_model(self, model: str) -> List[Prompt]:
        """Get prompts compatible with a specific model.
        
        Args:
            model: Model name to filter by
            
        Returns:
            List of compatible prompts
        """
        return self.settings.prompts.get_prompts_for_model(model)
    
    def update_prompt(
        self, 
        prompt_id: str, 
        name: Optional[str] = None,
        content: Optional[str] = None,
        language_model: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """Update an existing prompt.
        
        Args:
            prompt_id: ID of prompt to update
            name: New name (None to keep current)
            content: New content (None to keep current)
            language_model: New language model (None to keep current)
            description: New description (None to keep current)
            
        Returns:
            True if updated, False if prompt not found
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return False
            
        if name is not None:
            prompt.name = name
        if content is not None:
            prompt.content = content
        if language_model is not None:
            prompt.language_model = language_model
        if description is not None:
            prompt.description = description
            
        save_settings()
        return True
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by ID.
        
        Args:
            prompt_id: ID of prompt to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = self.settings.prompts.remove_prompt(prompt_id)
        if result:
            save_settings()
        return result
    
    def get_selected_prompt(self) -> Optional[Prompt]:
        """Get the currently selected prompt.
        
        Returns:
            Selected prompt or None
        """
        if not self.settings.prompts.selected_prompt_id:
            return None
        return self.get_prompt(self.settings.prompts.selected_prompt_id)
    
    def set_selected_prompt(self, prompt_id: Optional[str]) -> bool:
        """Set the currently selected prompt.
        
        Args:
            prompt_id: ID of prompt to select, or None to deselect
            
        Returns:
            True if set successfully, False if prompt not found
        """
        if prompt_id is not None and not self.get_prompt(prompt_id):
            return False
            
        self.settings.prompts.selected_prompt_id = prompt_id
        save_settings()
        return True
    
    def get_prompt_names(self, model: Optional[str] = None) -> List[tuple[str, str]]:
        """Get prompt names and IDs, optionally filtered by model.
        
        Args:
            model: Model name to filter by (None for all)
            
        Returns:
            List of (id, name) tuples
        """
        if model:
            prompts = self.get_prompts_for_model(model)
        else:
            prompts = self.get_all_prompts()
            
        return [(p.id, p.name) for p in prompts]
    
    def create_default_prompts(self) -> None:
        """Create default prompt templates if none exist."""
        if self.get_all_prompts():
            return  # Already have prompts
            
        default_prompts = [
            {
                "name": "Continue Writing",
                "content": "Please continue the following text in a natural and engaging way:",
                "language_model": "all",
                "description": "General purpose continuation prompt"
            },
            {
                "name": "Creative Story",
                "content": "Continue this creative story with vivid descriptions and compelling narrative:",
                "language_model": "all", 
                "description": "For creative fiction writing"
            },
            {
                "name": "Technical Documentation",
                "content": "Continue this technical documentation with clarity and precision:",
                "language_model": "all",
                "description": "For technical writing and documentation"
            },
            {
                "name": "Formal Writing",
                "content": "Continue this text in a formal, professional tone:",
                "language_model": "all",
                "description": "For business and academic writing"
            }
        ]
        
        for prompt_data in default_prompts:
            self.create_prompt(**prompt_data)


# Global prompt manager instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def initialize_default_prompts() -> None:
    """Initialize default prompts if none exist."""
    manager = get_prompt_manager()
    manager.create_default_prompts()