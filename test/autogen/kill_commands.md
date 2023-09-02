# Common Used Commands


## Start jobs in background

Using nohup:
```bash
nohup python test_prompt.py > log.out &
```
- "&" : running in the background
- "log.out" : file to save the output, by default it is nohup.out
- Other options: tmux, screen, etc.

## Kill jobs

## 1. kill with `jobs`
```bash
jobs
```
Get things like this: (job id, status, command)
```
[1]+  Done                    nohup python test/autogen/test_prompt.py
```
Kill jobs with job id:
```bash
kill %1
```

## 2. kill with `ps` and `kill`

Get the process id with name "test_prompt":
```bash
ps -aux | grep test_prompt
```
Example result: "1368782" is the process id
```
ykw5399  1368782  0.0  0.0 2260536 88528 pts/1   Rl   17:54   0:02 python test/autogen/test_prompt.py
```

Kill with process id:
```bash
kill 1368782
```


This command will kill all the processes with the name "test_prompt":
Be cautious if the matching name is too general. (for example, "python")
```bash
ps -aux | grep test_prompt | awk '{print $2}' | xargs -n 1 kill -9
```
