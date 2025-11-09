#!/usr/bin/env python3
"""
terminal_code_runner.py

Terminal Code-Runner — run a source file (or compile+run) based on its extension.

Usage:
  python terminal_code_runner.py path/to/file
  python terminal_code_runner.py path/to/file --yes         # skip confirmation
  python terminal_code_runner.py path/to/file --cwd /dir    # run in specific working dir

This mirrors the Lua/Neovim runner you provided:
- Maps many file extensions to a command that compiles/runs the file.
- For compiled languages it will compile and, on success, run the produced executable.
- Commands use shell so compile-and-run sequences (&&) work.

Security warning:
  This executes shell commands derived from file names and mapping templates.
  Do NOT run this script on untrusted input or files you don't control.
"""

from pathlib import Path
import argparse
import subprocess
import sys
import os
import shutil

# Colors (simple)
C_B = "\033[1;34m"
C_OK = "\033[1;32m"
C_WARN = "\033[1;33m"
C_ERR = "\033[1;31m"
C_RESET = "\033[0m"

BANNER = r"""
   _____           _       ______                            
  /  __ \         | |      | ___ \                           
  | /  \/ ___   __| | ___  | |_/ /   _ _ __  _ __   ___ _ __ 
  | |    / _ \ / _` |/ _ \ |    / | | | '_ \| '_ \ / _ \ '__|
  | \__/\ (_) | (_| |  __/ | |\ \ |_| | | | | | | |  __/ |   
   \____/\___/ \__,_|\___| \_| \_\__,_|_| |_|_| |_|\___|_|   
                                                          
                Terminal Code-Runner — run/build many languages
                         Made by Safin-Mohammad
"""

RUNNERS = {
    # interpreted / single-step
    "py":      'python3 "{file}"',
    "js":      'node "{file}"',
    "ts":      'ts-node "{file}"',
    "php":     'php "{file}"',
    "pl":      'perl "{file}"',
    "p6":      'perl6 "{file}"',
    "rb":      'ruby "{file}"',
    "go":      'go run "{file}"',
    "lua":     'lua "{file}"',
    "groovy":  'groovy "{file}"',
    "ps1":     'pwsh "{file}"',
    "bat":     '"{file}"',
    "cmd":     '"{file}"',
    "sh":      'bash "{file}"',
    "fsx":     'dotnet fsi "{file}"',
    "csx":     'dotnet script "{file}"',
    "vbs":     'cscript //nologo "{file}"',
    "coffee":  'coffee "{file}"',
    "scala":   'scala "{file}"',
    "swift":   'swift "{file}"',
    "jl":      'julia "{file}"',
    "cr":      'crystal run "{file}"',
    "ml":      'ocaml "{file}"',
    "r":       'Rscript "{file}"',
    "applescript": 'osascript "{file}"',
    "exs":     'elixir "{file}"',
    "clj":     'clojure "{file}"',
    "hx":      'haxe "{file}"',
    "rkt":     'racket "{file}"',
    "scm":     'scheme --script "{file}"',
    "ahk":     'autohotkey "{file}"',
    "au3":     'autoit3 "{file}"',
    "dart":    'dart "{file}"',
    "hs":      'runhaskell "{file}"',
    "nim":     'nim compile --run "{file}"',
    "d":       'ldc2 -run "{file}"',
    "lisp":    'sbcl --script "{file}"',
    "v":       'v run "{file}"',
    "zig":     'zig run "{file}"',
    "mojo":    'mojo run "{file}"',
    "scss":    'sass "{file}"',
    "sass":    'sass "{file}"',
    "less":    'lessc "{file}"',
    "ring":    'ring "{file}"',
    "pkl":     'pkl eval "{file}"',
    "spwn":    'spwn run "{file}"',
    "kit":     'kitc run "{file}"',
    "gleam":   'gleam run',
    # compiled / two-step (templates that produce an executable or runnable artifact)
    "c":       'gcc "{file}" -o "{name}" && "{run_path}"',
    "cpp":     'g++ "{file}" -o "{name}" && "{run_path}"',
    "java":    'javac "{file}" && java -cp "{cwd}" {name}',
    "kt":      'kotlinc "{file}" -include-runtime -d "{name}.jar" && java -jar "{name}.jar"',
    "cs":      'mcs "{file}" && mono "{name}.exe"',
    "m":       'clang "{file}" -o "{name}" && "{run_path}"',  # Objective-C / ObjC++
    "rs":      'rustc "{file}" -o "{name}" && "{run_path}"',
    "f90":     'gfortran "{file}" -o "{name}" && "{run_path}"',
    "cuda":    'nvcc "{file}" -o "{name}" && "{run_path}"',
    "pas":     'fpc "{file}" && "{run_path}"',
    "vb":      'vbc "{file}" && mono "{name}.exe"',
    "erl":     'erlc "{file}" && erl -noshell -s {name} start -s init stop',
}

def guess_runner(ext: str):
    return RUNNERS.get(ext.lower())

def make_run_path(name: str, cwd: Path):
    if os.name == "nt":
        exe = f"{name}.exe"
        return str(cwd / exe)
    else:
        return str(cwd / name)

def check_program_available(command_str: str):
    tokens = command_str.split()
    for tok in tokens:
        t = tok.strip('"').strip("'")
        if any(ch in t for ch in ['&', ';', '>', '|']) or t.startswith("{"):
            continue
        if t.startswith("-") or "=" in t:
            continue
        if any(c in t for c in ["/", "\\", "."]):
            continue
        return shutil.which(t) is not None
    return True

def run_file(path: Path, cwd: Path = None, assume_yes: bool = False):
    if not path.exists():
        print(f"{C_ERR}❌ File does not exist: {path}{C_RESET}")
        return 2

    ext = path.suffix.lstrip(".")
    name = path.stem
    cwd = Path(cwd) if cwd else path.parent.resolve()
    run_path = make_run_path(name, cwd)

    runner_template = guess_runner(ext)
    if runner_template is None:
        print(f"{C_ERR}❌ Unknown file type: .{ext}{C_RESET}")
        return 3

    cmd = runner_template.format(file=str(path), name=name, cwd=str(cwd), run_path=run_path)

    print(f"{C_B}{BANNER}{C_RESET}")
    print(f"{C_OK}▶ Running:{C_RESET} {cmd}")
    if not assume_yes:
        try:
            answer = input("Proceed? [Y/n] ").strip().lower()
        except KeyboardInterrupt:
            print("\nAborted.")
            return 1
        if answer not in ("", "y", "yes"):
            print("Aborted.")
            return 1

    if not check_program_available(cmd):
        print(f"{C_WARN}⚠️  Warning: required runtime/compiler may not found in PATH. Proceeding anyway.{C_RESET}")

    try:
        completed = subprocess.run(cmd, shell=True, cwd=str(cwd))
        rc = completed.returncode
        if rc == 0:
            print(f"\n{C_OK}✅ Command finished successfully (exit code 0).{C_RESET}")
        else:
            print(f"\n{C_ERR}❌ Command exited with code {rc}.{C_RESET}")
        return rc
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as exc:
        print(f"\n{C_ERR}❌ Execution failed: {exc}{C_RESET}")
        return 4

def main(argv=None):
    p = argparse.ArgumentParser(prog="terminal-code-runner", description="Terminal Code-Runner: run a source file based on extension.")
    p.add_argument("file", nargs="?", help="File to run (path).")
    p.add_argument("--cwd", help="Working directory to run in (default: file's parent).")
    p.add_argument("--yes", "-y", action="store_true", help="Don't ask for confirmation.")
    args = p.parse_args(argv)

    if not args.file:
        print("No file provided. Usage: python terminal_code_runner.py path/to/file")
        return 2

    path = Path(args.file)
    return run_file(path, cwd=args.cwd, assume_yes=args.yes)

if __name__ == "__main__":
    sys.exit(main())
