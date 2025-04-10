#!/usr/bin/env python3
"""
Daily Feed Reader
This script fetches RSS/Atom feeds from URLs specified in a YAML config file,
extracts relevant information, and saves it to a JSON or CSV file.
"""

import argparse
import csv
import feedparser
import json
import logging
import os
import time
import yaml
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser("~/feed_reader.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("feed_reader")

def load_config(config_path):
    """Load feed URLs from YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        raise

def parse_feed_date(entry):
    """Extract and standardize the publication date from a feed entry."""
    # Try different date fields that might be present
    date_fields = ['published', 'updated', 'pubDate', 'date']

    for field in date_fields:
        if field in entry and entry[field]:
            try:
                # Handle different date formats
                date_str = entry[field]
                if isinstance(date_str, str):
                    try:
                        # Try to parse as RFC 2822 format first (common in RSS)
                        return parsedate_to_datetime(date_str).isoformat()
                    except:
                        # Try to parse as ISO format or other common formats
                        dt = feedparser._parse_date(date_str)
                        if dt:
                            return dt.isoformat()
            except Exception as e:
                logger.warning(f"Failed to parse date {entry.get(field)}: {e}")

    # If no valid date found, use current time
    logger.warning(f"No valid date found for entry: {entry.get('title', 'Unknown')}")
    return datetime.now().isoformat()

def fetch_feeds(feed_urls):
    """Fetch and parse all feeds."""
    all_entries = []

    for feed_url in feed_urls:
        logger.info(f"Fetching feed: {feed_url}")
        try:
            # Add a small delay to be respectful to the servers
            time.sleep(1)

            feed = feedparser.parse(feed_url)

            if feed.bozo and hasattr(feed, 'bozo_exception'):
                logger.warning(f"Parsing error for {feed_url}: {feed.bozo_exception}")

            for entry in feed.entries:
                # Extract the required information
                item = {
                    'timestamp': parse_feed_date(entry),
                    'title': entry.get('title', 'No title'),
                    'author': entry.get('author', entry.get('creator', 'Unknown')),
                    'feed_url': feed_url,
                    'entry_url': entry.get('link', ''),
                }

                # Extract topics/categories if available
                if 'tags' in entry:
                    item['topics'] = [tag.get('term', tag.get('label', '')) for tag in entry.tags]
                elif 'categories' in entry:
                    item['topics'] = entry.categories
                else:
                    item['topics'] = []

                all_entries.append(item)

            logger.info(f"Processed {len(feed.entries)} entries from {feed_url}")

        except Exception as e:
            logger.error(f"Error processing feed {feed_url}: {e}")

    return all_entries

def save_to_json(entries, output_path):
    """Save entries to a JSON file."""
    try:
        # If file exists, load existing data and append new entries
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                existing_data = json.load(f)

            # Create a set of existing URLs to avoid duplicates
            existing_urls = {entry['entry_url'] for entry in existing_data if 'entry_url' in entry}

            # Only add entries with new URLs
            new_entries = [entry for entry in entries if entry['entry_url'] and entry['entry_url'] not in existing_urls]
            combined_entries = existing_data + new_entries

            logger.info(f"Added {len(new_entries)} new entries to existing {len(existing_data)} entries")
        else:
            combined_entries = entries
            logger.info(f"Created new JSON file with {len(entries)} entries")

        # Sort by timestamp (newest first)
        combined_entries.sort(key=lambda x: x['timestamp'], reverse=True)

        with open(output_path, 'w') as f:
            json.dump(combined_entries, f, indent=2)

        return len(combined_entries)

    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        raise

def save_to_csv(entries, output_path):
    """Save entries to a CSV file."""
    try:
        # Determine if we need to write headers (new file)
        file_exists = os.path.exists(output_path)

        if file_exists:
            # Read existing entries to avoid duplicates
            existing_entries = []
            with open(output_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                existing_entries = list(reader)

            # Create a set of existing URLs to avoid duplicates
            existing_urls = {entry['entry_url'] for entry in existing_entries if 'entry_url' in entry}

            # Only add entries with new URLs
            new_entries = [entry for entry in entries if entry['entry_url'] and entry['entry_url'] not in existing_urls]
            combined_entries = existing_entries + new_entries

            logger.info(f"Added {len(new_entries)} new entries to existing {len(existing_entries)} entries")
        else:
            combined_entries = entries
            logger.info(f"Created new CSV file with {len(entries)} entries")

        # Ensure all entries have the same fields
        fieldnames = ['timestamp', 'title', 'author', 'feed_url', 'entry_url', 'topics']

        # Convert list fields to strings for CSV
        for entry in combined_entries:
            if 'topics' in entry and isinstance(entry['topics'], list):
                entry['topics'] = ', '.join(entry['topics'])

        # Sort by timestamp (newest first)
        combined_entries.sort(key=lambda x: x['timestamp'], reverse=True)

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(combined_entries)

        return len(combined_entries)

    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Fetch and process RSS/Atom feeds.')
    parser.add_argument('--config', default='~/feed_config.yaml', help='Path to YAML config file')
    parser.add_argument('--output', default='~/feed_data.json', help='Path to output file (JSON or CSV)')
    args = parser.parse_args()

    # Expand user paths
    config_path = os.path.expanduser(args.config)
    output_path = os.path.expanduser(args.output)

    # Create parent directories if they don't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Load config
        config = load_config(config_path)
        feed_urls = config.get('feed_urls', [])

        if not feed_urls:
            logger.error("No feed URLs found in config file")
            return

        # Fetch feeds
        logger.info(f"Starting feed fetching process for {len(feed_urls)} feeds")
        entries = fetch_feeds(feed_urls)

        if not entries:
            logger.warning("No entries found in any feeds")
            return

        # Save to file based on extension
        output_ext = os.path.splitext(output_path)[1].lower()
        if output_ext == '.json':
            count = save_to_json(entries, output_path)
        elif output_ext == '.csv':
            count = save_to_csv(entries, output_path)
        else:
            logger.error(f"Unsupported output format: {output_ext}")
            return

        logger.info(f"Successfully processed {len(entries)} entries from {len(feed_urls)} feeds")
        logger.info(f"Output file now contains {count} entries: {output_path}")

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        raise

if __name__ == "__main__":
    main()
