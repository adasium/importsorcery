# importsorcery


## usage
```
python -m importsorcery \
       --index <project_directory> \
       --exclude <exclude_directory> <exclude_directory> \
       --symbol <symbol_to_import> \
       --current-file <currently_open_file>
```

| argument                            | description                                                  |
|-------------------------------------|--------------------------------------------------------------|
| `--symbol`, `--import-symbol`, `-s` | symbol to import                                             |
| `--exclude`, `-e`                   | directories that should not be traversed                     |
| `--index`                           | directory that should be scanned for imports                 |
| `--current-file`                    | currently opened file - required to suggest relative imports |
