# Code-Runner-vim

Code-Runner-vim is a small, practical helper script that detects a source file's extension and runs or compiles-and-runs it using sensible defaults. It supports dozens of languages and common compile-and-run sequences so you can quickly execute code from the terminal or wire it into your editor (e.g., Neovim).

Banner
```
   _____           _       ______                            
  /  __ \         | |      | ___ \                           
  | /  \/ ___   __| | ___  | |_/ /   _ _ __  _ __   ___ _ __ 
  | |    / _ \ / _` |/ _ \ |    / | | | '_ \| '_ \ / _ \ '__|
  | \__/\ (_) | (_| |  __/ | |\ \ |_| | | | | | | |  __/ |   
   \____/\___/ \__,_|\___| \_| \_\__,_|_| |_|_| |_|\___|_|   
                                                                                      
           Code-Runner-vim — run/build many languages
                   Made by Safin-Mohammad
```

Contents
- `terminal_code_runner.py` — main script that runs or builds-and-runs files based on extension.

Features
- Auto-detects the file extension and chooses an appropriate command to run or compile+run.
- Supports many languages (Python, JavaScript, TypeScript, C, C++, Rust, Java, Go, Ruby, PHP, Lua, etc.).
- For compiled languages runs a compile command and, on success, runs the produced artifact.
- Prints an ASCII banner and asks for confirmation (can be skipped with `--yes`).
- Small heuristic warning if a required runtime/compiler doesn't appear to be available.
- Designed to be easy to integrate with editors (Neovim, VSCode tasks, etc.).

Requirements
- Python 3.8+ to run the script.
- Language runtimes / compilers for languages you want to execute (e.g., python3, node, gcc, rustc, javac).
- Optional: `ts-node`, `dotnet`, `mono`, etc., depending on which language templates you use.

Installation
0. `git clone https://github.com/Safin-Mohammad/Code-Runner-vim`
1. `cd Code-Runner-vim`
2. Copy `terminal_code_runner.py` into your project or a bin directory on your PATH.
3. Make it executable (optional):
   ```
   chmod +x terminal_code_runner.py
   ```
4. Ensure needed runtimes/compilers are installed and on your PATH.

Basic usage
```
# Run a file (interactive confirmation)
python3 terminal_code_runner.py path/to/file

# Skip confirmation
python3 terminal_code_runner.py path/to/file --yes

# Run with a specific working directory
python3 terminal_code_runner.py path/to/file --cwd /path/to/working/dir
```

Examples
- Run a Python script:
  ```
  python3 terminal_code_runner.py hello.py
  ```
- Compile & run a C program:
  ```
  python3 terminal_code_runner.py hello.c
  ```
- Run a Java file (javac + java):
  ```
  python3 terminal_code_runner.py HelloWorld.java
  ```

Neovim integration (example)
You can wire the script to a keymap so it runs the current buffer in a split terminal:

```lua
-- place in your init.lua or a plugin file
vim.keymap.set('n', '<leader>r', function()
  local file = vim.fn.expand('%:p')
  if file == '' then
    print('No file to run')
    return
  end
  -- adjust path to terminal_code_runner.py if needed
  local runner = '/path/to/terminal_code_runner.py'
  vim.cmd('split term://python3 ' .. vim.fn.shellescape(runner) .. ' ' .. vim.fn.shellescape(file))
end, { desc = 'Run current file with Terminal Code-Runner' })
```

Customization
- Edit the `RUNNERS` dict inside `terminal_code_runner.py` to add or change per-extension templates.
- Templates are shell strings and may use these placeholders:
  - `{file}` — full path to the file
  - `{name}` — file stem (filename without extension)
  - `{cwd}` — working directory (file's parent by default)
  - `{run_path}` — path used to run compiled executables (handles .exe on Windows)
- If you prefer safer execution, replace `subprocess.run(..., shell=True)` with a tokenized command list and remove inline `&&` sequences; you can implement two-step compile+run flows in Python explicitly.

Security & legal
- This script constructs and executes shell commands — do NOT run it on untrusted files or input.
- Using `shell=True` is convenient for compile-and-run templates but increases risk; sandbox or inspect inputs in multiuser environments.
- Ensure you have permission to run or compile code in the environment where you use this tool.

Troubleshooting
- If the script warns that a runtime or compiler might be missing, verify you can run the command manually (e.g., `python3 --version`, `gcc --version`).
- For Java and Kotlin, ensure `javac` and `java` are on PATH and that the working directory is correct for classpath resolution.
- If compiled programs fail to execute on Windows, confirm `.exe` creation and the `cwd` parameter.

Contributing
- Add more language templates to `RUNNERS`.
- Improve runtime detection or replace the shell-based execution with safer, tokenized subprocess calls.
- Add per-project configuration (JSON/YAML) to override the default templates.

License
This project is provided under the MIT License.

- Original idea and Lua mapping inspired by Safin Mohammad's Neovim keymaps.

---
