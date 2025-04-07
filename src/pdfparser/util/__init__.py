
from .llmclient import LLMClient

def parse_args() -> dict[str, str]:
    import sys
    args = sys.argv[1:]
    if len(args) == 0:
        return {}
    res = {}
    arg_idx = 0
    for arg in args: 
        if arg.startswith("--"):
            arr = arg.split("=")
            key = arr[0][2:]  
            value = arr[1] if len(arr) > 1 else True
            res[key] = value
        elif arg.startswith("-"):
            key = arg[1:]
            res[key] = True
        else: 
            res[str(arg_idx)] = arg
            arg_idx += 1

    return res
