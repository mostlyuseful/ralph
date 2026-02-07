import json
import subprocess

def run_opencode(instructions: str, model: str|None = None):
    # proc = subprocess.Popen(
    #     [
    #         "opencode",
    #         "run",
    #         "--model",
    #         "openrouter/google/gemini-3-flash-preview",
    #         # "--format", "json",
    #         instructions,
    #     ],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.STDOUT,
    #     text=True,
    #     bufsize=1, # Line buffered
    # )
    # for line in proc.stdout: # type: ignore
    #     print(line, end="")
    #     #line = line.rstrip()
    #     # Each line is a JSON payload
    #     #payload = json.loads(line)
    # proc.wait()
    subprocess.run(
        [
            "opencode",
            "run",
            *(["--model", model] if model else []),
            instructions,
        ],
        check=True,
    )