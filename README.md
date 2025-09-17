# Worktree Manager

A Git worktree management tool that makes working with multiple branches easy and organized. Compatible with Linux, macOS, and Windows (WSL2).

## Overview

Worktree Manager is a Python-based tool that helps you create, manage, and switch between Git worktrees efficiently. It automatically organizes worktrees in a structured directory layout and provides seamless navigation between different branches of your projects.

## Features

- **Easy worktree creation**: Create new worktrees with a single command
- **Automatic branch management**: Creates branches if they don't exist locally, fetches from remote if available
- **Organized structure**: Keeps all worktrees in a dedicated directory structure
- **Shell integration**: Change directories automatically with the `wt` wrapper
- **Flexible configuration**: Customize paths and branch prefixes via environment variables
- **Multiple repository support**: Manage worktrees across different Git repositories

## Installation & Setup

1. **Clone the repository** to your preferred location (e.g., `~/Sources/command-line-utils/`):
   ```bash
   git clone https://github.com/mathd/worktree-manager.git ~/Sources/command-line-utils/worktree-manager
   ```

2. **Make the scripts executable:**
   ```bash
   cd ~/Sources/command-line-utils/worktree-manager
   chmod +x worktree-manager.py wt
   ```

3. **Configure environment variables** in your shell configuration file (`.zshrc`, `.bashrc`, etc.):
   ```bash
   # Set your projects directory
   export W_PROJECTS_DIR="$HOME/Sources"

   # Set your worktrees directory
   export W_WORKTREES_DIR="$HOME/Sources-Worktree"

   # Optional: Set a default branch prefix
   export W_DEFAULT_BRANCH_PREFIX="feature"
   ```

4. **Create an alias** for easy access. Add this to your shell configuration:
   ```bash
   alias wt='source "$HOME/Sources/command-line-utils/worktree-manager/wt"'
   ```

   **Note**: Replace the path with the actual location where you cloned the repository. Using `source` is crucial for the directory changing functionality to work properly.

5. **Reload your shell configuration:**
   ```bash
   source ~/.zshrc  # or ~/.bashrc
   ```

6. **Verify installation:**
   ```bash
   wt --where  # Should show your configured paths
   ```

## Usage

### Basic Commands

```bash
# Create or switch to a worktree (using shell wrapper)
wt feature-x

# Create or switch to a worktree (direct Python script)
./worktree-manager.py feature-x

# List worktrees for current repository
wt --list

# List all worktrees across all repositories
wt --list --all

# Remove a specific worktree
wt --rm feature-x

# Remove all worktrees for current repository
wt --clean

# Return to main repository
wt --home

# Show resolved paths (useful for debugging)
wt --where
```

### Shell Integration

The `wt` shell wrapper provides automatic directory changing:
- When creating or switching to a worktree, your shell automatically changes to that directory
- Use `source wt` or `. wt` to ensure the directory change persists in your current shell

### Running Commands in Worktrees

You can run commands directly in a worktree:
```bash
wt feature-x npm test
wt feature-x code .
```

## Configuration

The tool uses environment variables for configuration. These should be set in your shell configuration file (`.zshrc`, `.bashrc`, etc.):

```bash
# Directory where your main repositories are located
export W_PROJECTS_DIR="$HOME/Sources"

# Directory where worktrees will be created
export W_WORKTREES_DIR="$HOME/Sources-Worktree"

# Optional prefix for new branches (e.g., "feature" creates "feature/branch-name")
export W_DEFAULT_BRANCH_PREFIX="feature"

# Enable legacy worktree support (if needed)
export W_SUPPORT_LEGACY_CORE_WTS=1
```

**Important**: The tool creates worktrees based on the relative path of your repository within `W_PROJECTS_DIR`. For example, if you have a repo at `$HOME/Sources/my-project`, worktrees will be created in `$HOME/Sources-Worktree/my-project/`.

## Directory Structure

With the example configuration (`W_PROJECTS_DIR="$HOME/Sources"` and `W_WORKTREES_DIR="$HOME/Sources-Worktree"`), the tool organizes files like this:

```
~/Sources/
├── my-repo/                    # Main repository
│   ├── .git/
│   └── ...
└── command-line-utils/
    └── worktree-manager/
        ├── worktree-manager.py
        └── wt

~/Sources-Worktree/
└── my-repo/                   # Worktrees for my-repo
    ├── feature-x/             # Worktree for feature-x branch
    ├── bugfix-123/            # Worktree for bugfix-123 branch
    └── experiment/            # Worktree for experiment branch
```

## Requirements

- Python 3.6+
- Git
- Unix-like environment (Linux, macOS, WSL2)

## How It Works

1. **Worktree Creation**: When you specify a worktree name, the tool:
   - Creates the worktree directory structure if it doesn't exist
   - Checks if the branch exists locally or remotely
   - Fetches the branch from remote if available, or creates a new local branch
   - Creates the Git worktree using `git worktree add`

2. **Branch Naming**: Branch names are automatically processed:
   - Spaces are converted to hyphens
   - Optional prefix is added if configured
   - Leading/trailing slashes are stripped

3. **Shell Integration**: The `wt` wrapper:
   - Calls the Python script with your arguments
   - If the result is a valid directory path, changes to that directory
   - Otherwise, displays the output (for list commands, errors, etc.)

## Examples

```bash
# Create a new feature branch and worktree
wt "new feature"  # Creates branch: new-feature (or feature/new-feature with prefix)

# Work on an existing remote branch
wt hotfix-urgent  # Fetches and creates local worktree if branch exists on remote

# Quick development workflow
wt experiment
# ... make changes ...
wt --home         # Return to main repo
wt --rm experiment  # Clean up when done
```

## Troubleshooting

- **"Not in a git repository"**: Make sure you're running the command from within a Git repository
- **Permission denied**: Ensure the scripts are executable (`chmod +x worktree-manager.py wt`)
- **Command not found**: Add the script directory to your PATH or use the full path to the scripts
- **Directory changes don't persist**: Use `source wt` instead of `./wt` or ensure the `wt` wrapper is being used

## License

This project is open source. Feel free to use, modify, and distribute as needed.