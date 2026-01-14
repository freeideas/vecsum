# Download Compiler and Build Tools

Ensure the required compiler and build tools are available for building the project.

**First:** Read `./README.md` to determine which compiler/language the project uses. If it isn't obvious, then try reading `./specs/*.md` documents.

## Process

1. **Determine compiler and build tools** -- From README/specs, identify the required compiler/language, version, and any build tools (e.g., NSIS for installers)
2. **Always provision portable compiler** -- Download a portable/standalone build into `./tools/compiler/` even if one is already on PATH
3. **Verify the downloaded compiler** -- Run its version command from the downloaded location

## Requirements

- Do **not** rely on PATH; use the downloaded portable compiler
- Only if the WRONG compiler is in `./tools/compiler/`, delete that directory and replace it
- Download portable/standalone builds (not installers)
- Extract to `./tools/compiler/` directory
- Use the compiler from `./tools/compiler/` in build scripts
- The `./tools/` directory is gitignored

## Compiler Location

The compiler is always at `./tools/compiler/` (relative to the project root).

## Notes

- **C/C++ projects:** Use Zig as the compiler (`zig cc` / `zig c++`). Zig includes a drop-in C/C++ compiler that works cross-platform without additional setup.

- **Rust on Windows:** Use the GNU toolchain to avoid MSVC/Visual Studio dependencies:

  1. **Install Rust with GNU toolchain** (not MSVC):
     ```bash
     export RUSTUP_HOME=./tools/compiler/rustup
     export CARGO_HOME=./tools/compiler/cargo
     curl -o rustup-init.exe https://win.rustup.rs/x86_64
     ./rustup-init.exe -y --default-toolchain stable-x86_64-pc-windows-gnu --no-modify-path
     ```

  2. **Download MinGW-w64** (provides the GNU linker):
     ```bash
     curl -L -o mingw.zip "https://github.com/brechtsanders/winlibs_mingw/releases/download/15.2.0posix-13.0.0-ucrt-r5/winlibs-x86_64-posix-seh-gcc-15.2.0-mingw-w64ucrt-13.0.0-r5.zip"
     unzip mingw.zip -d ./tools/
     # Creates ./tools/mingw64/
     ```

  3. **Configure linker** in `./code/.cargo/config.toml`:
     ```toml
     [target.x86_64-pc-windows-gnu]
     linker = "../tools/mingw64/bin/gcc.exe"
     ```

  4. **Build script** must add MinGW to PATH:
     ```python
     env['PATH'] = str(mingw_bin) + os.pathsep + env.get('PATH', '')
     ```

  **Why GNU over MSVC?** The MSVC target requires Visual Studio Build Tools or complex NuGet package setup (`msvcrt.lib`, Windows SDK). GNU target only needs MinGW-w64 -- one portable download.

## Examples

These are some of the compilers you may need to download portably:

| Tool     | Test Command       | Portable Location                      |
| -------- | ------------------ | -------------------------------------- |
| Rust     | `rustc --version`  | `./tools/compiler/cargo/bin/rustc.exe` |
| MinGW    | `gcc --version`    | `./tools/mingw64/bin/gcc.exe` (for Rust on Windows) |
| Zig      | `zig version`      | `./tools/compiler/zig/zig.exe`         |
| C#       | `dotnet --version` | `./tools/compiler/dotnet/dotnet.exe`   |
| Go       | `go version`       | `./tools/compiler/go/bin/go.exe`       |
| Java     | `javac -version`   | `./tools/compiler/jdk/bin/javac.exe`   |
| NSIS     | `makensis /VERSION`| `./tools/nsis/makensis.exe`            |
