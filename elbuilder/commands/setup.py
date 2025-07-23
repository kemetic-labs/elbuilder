from pathlib import Path

from elbuilder.core.config import ElBuilderConfig


def setup_command(config: ElBuilderConfig | None = None) -> None:
    """Setup elbuilder by adding shims to shell configuration."""
    config = config or ElBuilderConfig.make()
    versions_dir = config.versions_dir

    if not versions_dir.exists() or not any(versions_dir.iterdir()):
        print("Error: No PHP versions installed.")
        print("Please install a PHP version first using: elbuilder install <version>")
        return

    shims_dir = config.shims_dir
    php_shim = shims_dir / "php"
    if not php_shim.exists() or not php_shim.is_symlink():
        print("Warning: No active PHP version is set.")
        print("Run `elbuilder use <version>` to set an active version.")

    home = Path.home()
    shell_configs = [
        (home / ".zshrc", "Zsh"),
        (home / ".bashrc", "Bash"),
    ]

    elbuilder_export_line = f'export PATH="{shims_dir}:$PATH"'
    elbuilder_comment = "# Added by elbuilder"

    updated_configs = []
    already_configured = []
    existing_configs = []

    for config_file, shell_name in shell_configs:
        if config_file.exists():
            existing_configs.append((config_file, shell_name))
            content = config_file.read_text()

            if elbuilder_export_line in content:
                already_configured.append((config_file, shell_name))
                print(f"{shell_name} configuration ({config_file}) already contains elbuilder setup.")
                continue

            with config_file.open("a") as f:
                f.write(f"\n{elbuilder_comment}\n{elbuilder_export_line}\n")

            updated_configs.append((config_file, shell_name))
            print(f"Added elbuilder to {shell_name} configuration ({config_file}).")

    if updated_configs:
        print("\nelbuilder setup complete! To use elbuilder in your current shell, run:")
        for config_file, shell_name in updated_configs:
            print(f"  source {config_file}  # For {shell_name} users")
        print("\nOr restart your terminal.")
    elif already_configured:
        print("\nelbuilder is already configured in your shell. No changes needed.")
    elif not existing_configs:
        print("No shell configuration files found (.zshrc or .bashrc).")
        print("You may need to manually add the following to your shell configuration:")
        print(f"  {elbuilder_export_line}")
    else:
        print("Unexpected configuration state. You may need to manually add:")
        print(f"  {elbuilder_export_line}")
