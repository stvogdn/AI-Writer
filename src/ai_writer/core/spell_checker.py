"""Spell checking functionality for AI Writer."""

import re

# Try to import enchant for spell checking
try:
    import enchant
    ENCHANT_AVAILABLE = True
except ImportError:
    ENCHANT_AVAILABLE = False

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor, QTextDocument
from PyQt5.QtWidgets import QTextEdit


class SpellCheckWorker(QThread):
    """Background thread for spell checking text."""

    word_checked = pyqtSignal(int, int, bool, list)  # start, length, is_correct, suggestions
    checking_finished = pyqtSignal()

    def __init__(self, text: str, dictionary_tag: str = "en_US"):
        """Initialize the spell check worker.

        Args:
            text: Text to spell check
            dictionary_tag: Language dictionary to use
        """
        super().__init__()
        self.text = text
        self.dictionary_tag = dictionary_tag
        self._should_stop = False

    def run(self):
        """Run the spell check in background."""
        if not ENCHANT_AVAILABLE:
            return

        try:
            # Initialize dictionary
            dictionary = enchant.Dict(self.dictionary_tag)

            # Find all words with their positions
            word_pattern = re.compile(r'\b[a-zA-Z]+\b')

            for match in word_pattern.finditer(self.text):
                if self._should_stop:
                    break

                word = match.group()
                start = match.start()
                length = len(word)

                # Check if word is correct
                is_correct = dictionary.check(word)

                # Get suggestions if word is incorrect
                suggestions = []
                if not is_correct:
                    suggestions = dictionary.suggest(word)[:5]  # Limit to 5 suggestions

                # Emit result
                self.word_checked.emit(start, length, is_correct, suggestions)

        except Exception as e:
            print(f"Spell check error: {e}")
        finally:
            self.checking_finished.emit()

    def stop(self):
        """Stop the spell checking."""
        self._should_stop = True


class SpellChecker(QObject):
    """Spell checker for text editor integration."""

    def __init__(self, text_editor: QTextEdit, parent=None):
        """Initialize the spell checker.

        Args:
            text_editor: Text editor to integrate with
            parent: Parent object
        """
        super().__init__(parent)
        self.text_editor = text_editor
        self.dictionary_tag = "en_US"
        self.enabled = True
        self.highlight_color = QColor(255, 0, 0, 100)  # Semi-transparent red

        # Storage for misspelled words
        self.misspelled_words = {}  # {position: (length, suggestions)}

        # Worker thread
        self.worker = None

        # Format for highlighting misspelled words
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor(255, 0, 0))
        self.misspelled_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        # Connect to text changes
        self.text_editor.textChanged.connect(self._on_text_changed)

    def set_enabled(self, enabled: bool):
        """Enable or disable spell checking.

        Args:
            enabled: Whether spell checking should be enabled
        """
        self.enabled = enabled
        if not enabled:
            self.clear_highlights()
        else:
            self.check_spelling()

    def set_dictionary(self, dictionary_tag: str):
        """Set the spell check dictionary language.

        Args:
            dictionary_tag: Language dictionary tag (e.g., 'en_US', 'en_GB')
        """
        if ENCHANT_AVAILABLE and enchant.dict_exists(dictionary_tag):
            self.dictionary_tag = dictionary_tag
            if self.enabled:
                self.check_spelling()
        else:
            print(f"Dictionary '{dictionary_tag}' not available")

    def set_highlight_color(self, color: QColor):
        """Set the color for highlighting misspelled words.

        Args:
            color: Color for highlighting
        """
        self.highlight_color = color
        self.misspelled_format.setUnderlineColor(color)
        if self.enabled:
            self.apply_highlights()

    def check_spelling(self):
        """Start spell checking the current text."""
        if not ENCHANT_AVAILABLE or not self.enabled:
            return

        # Stop any existing worker
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        # Clear existing highlights
        self.misspelled_words.clear()

        # Start new spell check
        text = self.text_editor.toPlainText()
        if text.strip():
            self.worker = SpellCheckWorker(text, self.dictionary_tag)
            self.worker.word_checked.connect(self._on_word_checked)
            self.worker.checking_finished.connect(self._on_checking_finished)
            self.worker.start()

    def clear_highlights(self):
        """Clear all spell check highlights."""
        self.misspelled_words.clear()

        # Remove highlighting from text editor
        cursor = self.text_editor.textCursor()
        cursor.select(QTextCursor.Document)

        # Reset format
        format = QTextCharFormat()
        cursor.mergeCharFormat(format)

        # Clear selection
        cursor.clearSelection()
        self.text_editor.setTextCursor(cursor)

    def apply_highlights(self):
        """Apply highlights to all misspelled words."""
        if not self.enabled:
            return

        # Save current cursor position
        current_cursor = self.text_editor.textCursor()
        current_position = current_cursor.position()

        # Apply highlights
        for position, (length, suggestions) in self.misspelled_words.items():
            cursor = QTextCursor(self.text_editor.document())
            cursor.setPosition(position)
            cursor.setPosition(position + length, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(self.misspelled_format)

        # Restore cursor position
        cursor = QTextCursor(self.text_editor.document())
        cursor.setPosition(current_position)
        self.text_editor.setTextCursor(cursor)

    def get_word_at_position(self, position: int) -> Tuple[str, int, int]:
        """Get the word at the specified position.

        Args:
            position: Character position in the text

        Returns:
            Tuple of (word, start_position, length)
        """
        text = self.text_editor.toPlainText()

        # Find word boundaries
        start = position
        while start > 0 and text[start - 1].isalpha():
            start -= 1

        end = position
        while end < len(text) and text[end].isalpha():
            end += 1

        word = text[start:end]
        return word, start, end - start
    
    def get_suggestions_for_position(self, position: int) -> List[str]:
        """Get spell check suggestions for word at position.
        
        Args:
            position: Character position in the text
            
        Returns:
            List of suggestions for the word at that position
        """
        for word_pos, (length, suggestions) in self.misspelled_words.items():
            if word_pos <= position < word_pos + length:
                return suggestions
        return []
    
    def replace_word_at_position(self, position: int, new_word: str):
        """Replace the word at the specified position.
        
        Args:
            position: Character position in the text
            new_word: Replacement word
        """
        word, start, length = self.get_word_at_position(position)

        if word:
            cursor = QTextCursor(self.text_editor.document())
            cursor.setPosition(start)
            cursor.setPosition(start + length, QTextCursor.KeepAnchor)
            cursor.insertText(new_word)

            # Remove from misspelled words if it was there
            if start in self.misspelled_words:
                del self.misspelled_words[start]
    
    def add_word_to_dictionary(self, word: str):
        """Add a word to the personal dictionary.
        
        Args:
            word: Word to add to dictionary
        """
        if ENCHANT_AVAILABLE:
            try:
                # This would require a personal word list implementation
                # For now, we just remove it from current misspellings
                text = self.text_editor.toPlainText()
                positions_to_remove = []

                for pos, (length, suggestions) in self.misspelled_words.items():
                    if text[pos:pos + length].lower() == word.lower():
                        positions_to_remove.append(pos)

                for pos in positions_to_remove:
                    del self.misspelled_words[pos]

                self.apply_highlights()
            except Exception as e:
                print(f"Error adding word to dictionary: {e}")
    
    def _on_text_changed(self):
        """Handle text editor content changes."""
        if self.enabled:
            # Debounce spell checking to avoid checking on every keystroke
            # This would be better with a QTimer for proper debouncing
            self.check_spelling()
    
    def _on_word_checked(self, start: int, length: int, is_correct: bool, suggestions: List[str]):
        """Handle word check result from worker thread.
        
        Args:
            start: Start position of the word
            length: Length of the word
            is_correct: Whether the word is spelled correctly
            suggestions: List of spelling suggestions
        """
        if not is_correct:
            self.misspelled_words[start] = (length, suggestions)
    
    def _on_checking_finished(self):
        """Handle spell checking completion."""
        if self.enabled:
            self.apply_highlights()
    
    @staticmethod
    def is_available() -> bool:
        """Check if spell checking is available.
        
        Returns:
            True if PyEnchant is available
        """
        return ENCHANT_AVAILABLE
    
    @staticmethod
    def get_available_languages() -> List[str]:
        """Get list of available spell check languages.
        
        Returns:
            List of available language tags
        """
        if not ENCHANT_AVAILABLE:
            return []

        try:
            return enchant.list_dicts()
        except:
            return ["en_US"]  # Fallback