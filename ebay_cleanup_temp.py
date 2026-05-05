#!/usr/bin/env python3
"""
eBay Temporary Test Output Cleanup
Auto-deletes production API test files older than 7 days.

This maintains compliance with our exemption statement:
"We do not persist eBay data."
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone


def cleanup_old_files(directory="data/ebay_active_search", max_age_days=7, dry_run=False):
    """
    Delete files older than max_age_days.
    
    Args:
        directory: Directory to clean
        max_age_days: Maximum file age in days
        dry_run: If True, only show what would be deleted
    """
    target_dir = Path(directory)
    
    if not target_dir.exists():
        print(f"Directory does not exist: {target_dir}")
        return
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    
    files_to_delete = []
    
    # Find old files
    for file_path in target_dir.glob("*"):
        if not file_path.is_file():
            continue
        
        # Get file modification time
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        
        if file_mtime < cutoff_time:
            files_to_delete.append((file_path, file_mtime))
    
    # Sort by age (oldest first)
    files_to_delete.sort(key=lambda x: x[1])
    
    if not files_to_delete:
        print(f"✓ No files older than {max_age_days} days found in {target_dir}")
        return
    
    print(f"Found {len(files_to_delete)} file(s) older than {max_age_days} days:")
    print()
    
    total_size = 0
    
    for file_path, file_mtime in files_to_delete:
        age_days = (datetime.now(timezone.utc) - file_mtime).days
        file_size = file_path.stat().st_size
        total_size += file_size
        
        size_str = format_size(file_size)
        print(f"  {file_path.name}")
        print(f"    Age: {age_days} days | Size: {size_str}")
        print()
    
    print(f"Total size: {format_size(total_size)}")
    print()
    
    if dry_run:
        print("DRY RUN - No files deleted")
        print("Run without --dry-run to actually delete these files")
    else:
        # Confirm deletion
        response = input(f"Delete {len(files_to_delete)} file(s)? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return
        
        # Delete files
        deleted_count = 0
        for file_path, _ in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"✗ Failed to delete {file_path.name}: {e}")
        
        print(f"✓ Deleted {deleted_count} file(s)")


def format_size(size_bytes):
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up temporary eBay API test output files older than 7 days",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ebay_cleanup_temp.py --dry-run
  python ebay_cleanup_temp.py --max-age 7
  python ebay_cleanup_temp.py --max-age 3
        """
    )
    
    parser.add_argument("--directory", default="data/ebay_active_search", 
                        help="Directory to clean (default: data/ebay_active_search)")
    parser.add_argument("--max-age", type=int, default=7, 
                        help="Maximum file age in days (default: 7)")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Show what would be deleted without actually deleting")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("eBay Temporary Test Output Cleanup")
    print("=" * 70)
    print(f"Directory: {args.directory}")
    print(f"Max Age: {args.max_age} days")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    cleanup_old_files(args.directory, args.max_age, args.dry_run)


if __name__ == "__main__":
    main()
