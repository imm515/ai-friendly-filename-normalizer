# AI-Friendly Filename Normalizer

A Python tool for batch normalizing filenames, designed for AI/ML data preprocessing. Recursively processes all files and folders in a directory.

## Features

- ✅ Recursive processing of all subdirectories
- ✅ Convert full-width characters to half-width (spaces, hyphens, brackets, etc.)
- ✅ Replace spaces and hyphens with underscores
- ✅ Double underscore separators around brackets for better readability
- ✅ Merge consecutive underscores
- ✅ Dry-run mode (preview)
- ✅ Detailed logging output
- ✅ Command-line argument support

## Usage

### Basic Usage

```bash
# Process current directory
python ai_friendly_filename_normalizer.py

# Process specified directory
python ai_friendly_filename_normalizer.py -d /path/to/dir

# Dry-run mode (preview only, no actual execution)
python ai_friendly_filename_normalizer.py --dry-run

# Combined usage
python ai_friendly_filename_normalizer.py -d /path/to/dir --dry-run
```

### Parameters

- `-d, --dir`: Directory path to process (default: current directory)
- `--dry-run`: Dry-run mode, only show operations to be performed, no actual execution

## Processing Rules

The script normalizes filenames according to these rules:

1. **Full-width to Half-width Conversion**
   - `　` (full-width space) → ` ` (half-width space) → `_` (underscore)
   - `—` `–` (full-width hyphen) → `-` (half-width hyphen) → `_` (underscore)
   - `【` `】` (full-width brackets) → `__[` `]__` (double underscore separator)
   - `（` `）` (full-width parentheses) → `__(` `)__` (double underscore separator)

2. **Replace with Underscore**
   - Space ` ` → `_`
   - Hyphen `-` → `_`

3. **Preserve Other Characters**
   - Chinese, English, numbers, dots
   - Brackets `[` `]`, parentheses `(` `)` (with underscore separators)
   - Other special characters like `@` `#` `*` `%` etc.

4. **Cleanup Optimization**
   - Merge consecutive underscores into one
   - Remove leading and trailing underscores
   - Preserve file extensions

## Examples

### Before
```
report-2026-summary【final】version.docx
data analysis-results 2025.xlsx
document（draft）.pdf
project files/data set/
test@file#2024.txt
```

### After
```
report_2026_summary__[final]__version.docx
data_analysis_results_2025.xlsx
document__(draft).pdf
project_files/data_set/
test@file#2024.txt
```

**Note:**
- Only spaces and hyphens are replaced with underscores
- Full-width brackets `【】` are converted to `__[ ]__` (double underscore separator)
- Full-width parentheses `（）` are converted to `__( )__` (double underscore separator)
- Other special characters (@, #, etc.) remain unchanged

## Why AI-Friendly?

This tool optimizes filenames for AI/ML analysis:

1. **Unified Encoding**: Convert full-width to half-width, reducing tokenization issues
2. **Clear Boundaries**: Double underscore separators provide clear word boundaries
3. **Remove Special Characters**: Reduce NLP processing errors
4. **Standardized Naming**: Facilitate feature extraction

## Log Output

The script outputs detailed log information:

- Processing start time and target directory
- Running mode (dry-run/formal execution)
- Number of items to rename
- Processing result for each file (success/skip/fail)
- Final statistics

### Example Log

```
2026-03-29 09:09:54 - INFO - ============================================================
2026-03-29 09:09:54 - INFO - Processing directory: /path/to/directory
2026-03-29 09:09:54 - INFO - Running mode: formal execution
2026-03-29 09:09:54 - INFO - ============================================================
2026-03-29 09:09:54 - INFO - Found 6 items to rename
2026-03-29 09:09:54 - INFO - ------------------------------------------------------------
2026-03-29 09:09:54 - INFO - ✓ Rename successful: old-file.doc -> new_file.doc
2026-03-29 09:09:54 - INFO - ============================================================
2026-03-29 09:09:54 - INFO - Processing complete! Statistics:
2026-03-29 09:09:54 - INFO -   Successfully renamed: 6
2026-03-29 09:09:54 - INFO -   Skipped: 0
2026-03-29 09:09:54 - INFO -   Failed: 0
2026-03-29 09:09:54 - INFO - ============================================================
```

## Technical Features

- **Depth-First Traversal**: Process subdirectories before parent directories to avoid path invalidation
- **Path Safety**: Use `pathlib` for path handling, cross-platform compatible
- **Exception Handling**: Catch and log all errors, won't interrupt due to single file failure
- **Idempotency**: Can be run multiple times, already normalized files will be skipped

## System Requirements

- Python 3.6+
- No additional dependencies (standard library only)

## Use Cases

- AI/ML data preprocessing
- Document management systems
- File batch processing
- Data cleaning pipelines
- Cross-platform file synchronization

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Generated with CodeBuddy AI assistance
