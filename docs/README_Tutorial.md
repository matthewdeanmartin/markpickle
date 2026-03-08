# Markpickle Tutorial

This is an interactive Jupyter notebook that teaches you how to use Markpickle - a Python library for lossy serialization of Python data types to Markdown and back.

## What you'll learn

1. **Introduction to Markpickle**: What it is, key features, and use cases
2. **Installation**: How to install Markpickle using pip
3. **Basic Usage**: Serializing Python objects to Markdown and deserializing Markdown back to Python
4. **Working with Different Data Types**: Scalars, lists, dictionaries, lists of dictionaries, and binary data
5. **Advanced Configuration**: Customizing serialization behavior with Config class
6. **Working with Files**: Reading and writing Markdown files
7. **Multiple Documents**: Handling multiple documents in a single Markdown file
8. **Command-Line Usage**: Using Markpickle from the terminal
9. **Real-World Scenarios**: Converting API responses to Markdown documentation
10. **Limitations and Best Practices**: Understanding lossy serialization and best practices

## Getting Started

1. **Install Jupyter Notebook**: If you don't have Jupyter installed, you can install it with:
   ```bash
   pip install jupyter
   ```

2. **Open the Notebook**:
   ```bash
   jupyter notebook docs/Markpickle_Tutorial.ipynb
   ```

3. **Run the Cells**: Click on each cell and press Shift+Enter to run the code.

## Prerequisites

- Python 3.8 or higher
- Markpickle library
- Jupyter Notebook or JupyterLab

## Files in this Tutorial

- **docs/Markpickle_Tutorial.ipynb**: Main tutorial notebook (unexecuted)
- **docs/Markpickle_Tutorial_Executed.ipynb**: Notebook with all cells executed

## How to Execute the Notebook

To run the notebook and see the outputs, you can execute it from the command line:

```bash
jupyter nbconvert --to notebook --execute docs/Markpickle_Tutorial.ipynb --output Markpickle_Tutorial_Executed --output-dir docs
```

## Note

Markpickle is a lossy serialization library, which means not all Python types can be perfectly serialized and deserialized. Some information may be lost during the process.

## Resources

- [Markpickle GitHub Repository](https://github.com/matthewdeanmartin/markpickle)
- [Markpickle Documentation](https://github.com/matthewdeanmartin/markpickle/blob/main/README.md)
- [Markpickle on PyPI](https://pypi.org/project/markpickle/)