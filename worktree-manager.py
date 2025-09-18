#!/usr/bin/env python3
"""
Worktree Manager (Python) — v1
A Git worktree management tool.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


# Configuration from environment
PROJECTS_DIR = Path(os.environ.get('W_PROJECTS_DIR', Path.home() / 'projects'))
WORKTREES_DIR = Path(os.environ.get('W_WORKTREES_DIR', Path.home() / 'projects' / 'worktrees'))
BRANCH_PREFIX = os.environ.get('W_DEFAULT_BRANCH_PREFIX', '')
SUPPORT_LEGACY = bool(os.environ.get('W_SUPPORT_LEGACY_CORE_WTS', ''))


def run_git(cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = True, check: bool = True):
    """Run a git command with error handling."""
    try:
        return subprocess.run(['git'] + cmd, cwd=cwd, capture_output=capture_output, text=True, check=check, encoding='utf-8', errors='replace')
    except subprocess.CalledProcessError as e:
        if check:
            print(f"Git error: {e.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        return e


def die(msg: str) -> None:
    """Print error and exit."""
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)

def get_repo_root() -> Optional[Path]:
    """Get the root of the current git repository."""
    result = run_git(['rev-parse', '--show-toplevel'], check=False)
    return Path(result.stdout.strip()) if result.returncode == 0 else None


def resolve_paths():
    """Get repo root and worktree base directory."""
    repo_root = get_repo_root()
    if not repo_root:
        die("Not in a git repository")

    try:
        repo_rel = str(repo_root.relative_to(PROJECTS_DIR))
    except ValueError:
        repo_rel = repo_root.name

    return repo_root, WORKTREES_DIR / repo_rel


def build_branch_name(name: str) -> str:
    """Build branch name with optional prefix."""
    name = name.replace(' ', '-').strip('/')
    return f"{BRANCH_PREFIX.rstrip('/')}/{name}" if BRANCH_PREFIX else name


def ensure_branch(branch: str, repo_root: Path) -> None:
    """Ensure branch exists locally."""
    if run_git(['show-ref', '--verify', '--quiet', f'refs/heads/{branch}'], cwd=repo_root, check=False).returncode == 0:
        return

    if run_git(['ls-remote', '--exit-code', '--heads', 'origin', branch], cwd=repo_root, check=False).returncode == 0:
        run_git(['fetch', 'origin', f'{branch}:{branch}'], cwd=repo_root)
    else:
        run_git(['branch', branch], cwd=repo_root)

# Command functions
def cmd_where():
    """Show resolved paths."""
    repo_root, wts_base = resolve_paths()
    print(f"{repo_root}\n{wts_base}")


def cmd_list(all_repos: bool = False):
    """List worktrees."""
    if all_repos:
        print("=== All Worktrees ===")
        if WORKTREES_DIR.exists():
            for repo_dir in WORKTREES_DIR.iterdir():
                if repo_dir.is_dir() and any(repo_dir.iterdir()):
                    print(f"[{repo_dir.name}]")
                    for wt in repo_dir.iterdir():
                        if wt.is_dir():
                            print(f"  • {wt.name}")
                    print()
        return

    _, wts_base = resolve_paths()
    print("=== Worktrees for current repo ===")

    if wts_base.exists():
        for wt in wts_base.iterdir():
            if wt.is_dir():
                print(f"  • {wt.name}")


def cmd_remove(worktree: str, force: bool = False):
    """Remove a worktree."""
    repo_root, wts_base = resolve_paths()
    wt_path = wts_base / worktree

    if not wt_path.exists():
        die(f"Worktree not found: {wt_path}")

    cmd = ['worktree', 'remove']
    if force:
        cmd.append('--force')
    cmd.append(str(wt_path))

    run_git(cmd, cwd=repo_root)
    print(f"Removed worktree: {worktree}")


def cmd_clean():
    """Remove all worktrees for current repository."""
    repo_root, wts_base = resolve_paths()

    if not wts_base.exists():
        print("No worktrees to clean")
        return

    count = 0
    for wt_path in wts_base.iterdir():
        if wt_path.is_dir():
            print(f"Removing worktree: {wt_path.name}")
            if run_git(['worktree', 'remove', str(wt_path)], cwd=repo_root, check=False).returncode == 0:
                count += 1

    print(f"Cleaned {count} worktree(s)" if count > 0 else "No worktrees were removed")


def cmd_home():
    """Return to main repository."""
    result = run_git(['worktree', 'list', '--porcelain'], check=False)
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if line.startswith('worktree '):
                main_repo = Path(line.split(' ', 1)[1])
                print(str(main_repo))
                return

    repo_root = get_repo_root()
    if repo_root:
        print(str(repo_root))
    else:
        die("Could not find main repository")


def cmd_create_or_switch(worktree: str, command: Optional[List[str]] = None):
    """Create worktree if needed and switch to it."""
    repo_root, wts_base = resolve_paths()
    wts_base.mkdir(parents=True, exist_ok=True)

    name = worktree.replace(' ', '-').strip('/')
    if not name:
        die("Invalid worktree name")

    branch_name = build_branch_name(name)
    wt_path = wts_base / name

    if not wt_path.exists():
        print(f"Creating worktree: {wt_path} (branch: {branch_name})", file=sys.stderr)
        run_git(['fetch', '--all', '--prune'], cwd=repo_root, check=False)
        ensure_branch(branch_name, repo_root)
        run_git(['worktree', 'add', str(wt_path), branch_name], cwd=repo_root)

    if command:
        old_cwd = Path.cwd()
        try:
            os.chdir(wt_path)
            return subprocess.run(command, shell=len(command) == 1, encoding='utf-8', errors='replace').returncode
        finally:
            os.chdir(old_cwd)
    else:
        # Output just the path for shell to use
        print(str(wt_path))
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Git worktree manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s feature-x           # Create/switch to worktree 'feature-x'
  %(prog)s --list              # List worktrees for current repo
  %(prog)s --list --all        # List all worktrees
  %(prog)s --rm feature-x      # Remove worktree 'feature-x'
  %(prog)s --clean             # Remove all worktrees for current repo
  %(prog)s --home              # Return to main repository
        """
    )

    parser.add_argument('--where', action='store_true', help='Show resolved paths')
    parser.add_argument('--list', action='store_true', help='List worktrees')
    parser.add_argument('--all', action='store_true', help='List all worktrees (use with --list)')
    parser.add_argument('--rm', metavar='WORKTREE', help='Remove a worktree')
    parser.add_argument('--force', action='store_true', help='Force removal (use with --rm)')
    parser.add_argument('--clean', action='store_true', help='Remove all worktrees for current repo')
    parser.add_argument('--home', action='store_true', help='Return to main repository')
    parser.add_argument('worktree', nargs='?', help='Worktree name')
    parser.add_argument('command', nargs='*', help='Command to run in worktree')

    args = parser.parse_args()

    try:
        if args.where:
            cmd_where()
        elif args.list:
            cmd_list(all_repos=args.all)
        elif args.rm:
            cmd_remove(args.rm, force=args.force)
        elif args.clean:
            cmd_clean()
        elif args.home:
            cmd_home()
        elif args.worktree:
            return cmd_create_or_switch(args.worktree, args.command)
        else:
            parser.print_help()
            return 1
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130


if __name__ == '__main__':
    sys.exit(main())