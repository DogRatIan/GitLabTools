# GitLab related tools


## python_scripts/clone_v3_projects.py

Clone all projects from an old GitLab server (V3 API). A list.json will generate and contains all project information.
```
python python_scripts/clone_v3_projects.py [OPTIONS] OUTPUT_DIR
    -t TOKEN, --token=TOKEN             Set API token
    -s SERVER, --server=SERVER          Set server address
    -u USERNAME, --user=USERNAME        Set HTTPS username
    -p PASSWORD, --password=PASSWORD    Set HTTPS password
    -a, --actualRun                     Without this, the clone action will skip.
    -h, --help                          Show this help.
```

Example:
```
python clone_v3_projects.py -t 123456 -h git.host.com:443 -u admin -p 1234 -a
```

## python_scripts/clone_v4_projects.py

Clone all projects from a GitLab server (V4 API). A list.json will generate and contains all project information.
```
python clone_v4_projects.py [OPTIONS] OUTPUT_DIR
    -t TOKEN, --token=TOKEN             Set API token
    -s SERVER, --server=SERVER          Set server address
    -u USERNAME, --user=USERNAME        Set HTTPS username
    -a, --actualRun                     Without this, the clone action will skip.
    -h, --help                          Show this help.
```

Example:
```
python clone_v4_projects.py -t 123456 -h git.host.com:8080 -u admin -a
```

## python_scripts/push_v4_projects.py

Push projects to a GitLab server (V4 API). The project list is based on the list.json file under the input directory.
```
python push_v4_projects.py [OPTIONS] INPUT_DIR
    -t TOKEN, --token=TOKEN             Set API token
    -s SERVER, --server=SERVER          Set server address
    -u USERNAME, --user=USERNAME        Set HTTPS username
    -a, --actualRun                     Without this, the push action will skip.
    -h, --help                          Show this help.
 
Example: 
```

Example:
```
python push_v4_projects.py -t 123456 -h git.host.com:8080 -u admin -a
```
