# AI Writer User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Features](#features)
- [Settings](#settings)
- [Troubleshooting](#troubleshooting)
- [Tips and Tricks](#tips-and-tricks)

## Getting Started

### Installation

1. **Install Ollama** (required for AI functionality):
   - Visit [ollama.ai](https://ollama.ai) and download for your OS
   - Start Ollama: `ollama serve`
   - Install a model: `ollama pull llama2`

2. **Install AI Writer**:

   ```bash
   pip install ai-writer
   ```

3. **Launch the application**:

   ```bash
   ai-writer
   ```

### First Launch

When you first open AI Writer:

1. The app will scan for available Ollama models
2. Select a model from the dropdown menu
3. Start writing in the main text area
4. Click "Generate" to let AI continue your text

## Basic Usage

### Writing with AI Assistance

1. **Start writing** your document in the main text area
2. **Position your cursor** where you want the AI to continue
3. **Adjust settings** in the sidebar if needed:
   - Temperature (creativity vs. focus)
   - Token limit (length of AI response)
4. **Click "Generate"** to let the AI continue your writing
5. **Review and edit** the AI-generated text as needed

### Saving Your Work

- **Save as Text**: Click the "📄 Save .txt" button
- **Save as Word**: Click the "📕 Save .docx" button (requires python-docx)
- Files are automatically named with timestamp

## Features

### AI Text Generation

- **Model Selection**: Choose from any installed Ollama models
- **Smart Continuation**: AI understands context and continues naturally
- **Cursor-based**: AI continues from your cursor position
- **No Repetition**: Built-in logic prevents repeating existing text

### User Interface

- **Light/Dark Themes**: Toggle with the 🌙/☀️ button
- **Responsive Layout**: Sidebar with controls, main editor area
- **Character Count**: Real-time character count in toolbar
- **Status Updates**: Progress and error messages in status bar

### File Support

- **Plain Text (.txt)**: Universal format, always available
- **Word Documents (.docx)**: Rich format when python-docx is installed
- **Auto-naming**: Files automatically named with timestamps

## Settings

### Temperature Control

Controls the creativity vs. focus balance of AI generation:

- **🎯 Low (0.0-0.3)**: More focused, consistent, predictable
- **⚖️ Medium (0.4-0.8)**: Balanced creativity and coherence  
- **🎨 High (0.9-2.0)**: More creative, diverse, experimental

### Token Limit

Controls the length of AI responses:

- **Low (10-50)**: Short continuations, sentence fragments
- **Medium (50-200)**: Paragraph-length responses
- **High (200-2000)**: Long-form continuations

### Model Selection

Different models have different strengths:

- **llama2**: Good general-purpose model
- **codellama**: Better for technical/programming content
- **mistral**: Fast and efficient for most tasks
- **Custom models**: Any model you've installed with Ollama

## Troubleshooting

### Common Issues

**"Cannot connect to Ollama" error:**

- Make sure Ollama is running: `ollama serve`
- Check if Ollama is on a different port (default: 11434)
- Restart Ollama service

**"No models found":**

- Install a model: `ollama pull llama2`
- Click the refresh button 🔄 to rescan
- Verify models are listed: `ollama list`

**"Generation failed" errors:**

- Try a different model
- Reduce token limit if out of memory
- Check Ollama logs for detailed errors

**Save buttons disabled:**

- Make sure you have text in the editor
- For .docx saving, install: `pip install python-docx`

### Performance Issues

**Slow generation:**

- Use smaller models (7B vs 13B parameters)
- Reduce token limit
- Lower temperature slightly
- Ensure sufficient RAM/VRAM

**UI freezing:**

- Generation runs in background threads
- If UI freezes, restart the application
- Check system resources

### Configuration

Settings are automatically saved to:

- **Windows**: `%APPDATA%\AI-Writer\settings.json`
- **macOS/Linux**: `~/.config/ai-writer/settings.json`

You can manually edit this file to customize advanced settings.

## Tips and Tricks

### Writing Effectively

1. **Start with context**: Give the AI some context before asking it to continue
2. **Use clear sentences**: Complete thoughts work better than fragments
3. **Position cursor carefully**: Place cursor exactly where you want continuation
4. **Iterate and refine**: Generate, edit, and generate again for best results

### Managing Creativity

- **Lower temperature** for factual content, technical writing
- **Higher temperature** for creative fiction, brainstorming
- **Adjust token limit** based on how much text you want generated

### Workflow Tips

1. **Save frequently**: Use Ctrl+S habit or save after major sections
2. **Use themes**: Switch to dark mode for reduced eye strain
3. **Model switching**: Try different models for different writing styles
4. **Backup important work**: Consider version control for important documents

### Keyboard Shortcuts

While AI Writer doesn't currently implement custom shortcuts, you can use standard text editing shortcuts:

- **Ctrl+A**: Select all
- **Ctrl+C/V**: Copy/paste
- **Ctrl+Z**: Undo
- **Ctrl+F**: Find (browser-style)

### Advanced Usage

**Custom prompting techniques:**

- End sentences with specific words to guide continuation
- Use formatting cues (bullet points, headers) to guide structure
- Include style instructions in your text

**Model comparison:**

- Try the same continuation with different models
- Compare creativity levels and writing styles
- Use specialized models for specific content types

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **Ollama Documentation**: For model-specific questions  
- **Community**: Share tips and get help from other users

Remember: AI Writer is a tool to enhance your writing, not replace it. The best results come from collaboration between human creativity and AI assistance!\n
