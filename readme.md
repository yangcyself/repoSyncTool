This project is a simple tool that sync some files between different git repos

To sync once, just configue the configuration file and then run the script
```bash
python syncTool.py
```

The configuration file is called `synclist.json`

below is a typical format of synclist
```json
{
    "repo1_path": "<git_repo1>",
    "repo2_path": "<git_repo2>",
    "sync_pairs":[{
        "file_name1": "<relative_file_name_or_path>",
        "file_name2": "<relative_file_name_or_path>"
    },{
        "file_name1": "<relative_path_to_sync>",
        "file_name2": "<relative_path_to_sync>"
    }]
}
```
