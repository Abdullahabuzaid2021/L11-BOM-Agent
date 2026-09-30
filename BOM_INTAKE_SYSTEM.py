"""
BOM Intake System
Automated monitoring and processing of new BOM files
Handles file validation, duplicate detection, and processing queue management
"""

import json
import logging
import hashlib
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum


class FileStatus(Enum):
    """File processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class BOMIntakeSystem:
    """
    Automated BOM intake system with file monitoring and processing queue
    Handles: monitoring, validation, duplicate detection, processing, versioning
    """

    def __init__(self, config_file="config/intake_config.json"):
        """Initialize intake system"""
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.intake_config = self.config['intake']

        # Setup directories
        self.dirs = self._setup_directories()

        # File tracking
        self.file_registry = {}  # Track processed files
        self.processing_queue = []
        self.file_fingerprints = {}  # Detect duplicates

        # Logger
        self.logger = self._setup_logging()

        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None

    def _setup_logging(self):
        """Setup logging to file and console"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # File handler
        log_file = self.dirs['log'] / f"intake_{datetime.now().strftime('%Y%m%d')}.log"
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def _load_config(self):
        """Load configuration from JSON"""
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def _setup_directories(self):
        """Create required directory structure"""
        dirs = {}
        for dir_key, dir_path in self.intake_config['directories'].items():
            path = Path(dir_path)
            path.mkdir(parents=True, exist_ok=True)
            dirs[dir_key.replace('_directory', '')] = path

        self.logger.info(f"✅ Directory structure initialized")
        return dirs

    def _calculate_fingerprint(self, file_path):
        """Calculate file fingerprint for duplicate detection"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _validate_file(self, file_path):
        """Validate file before processing"""
        file_path = Path(file_path)

        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # File exists
        if not file_path.exists():
            validation_results['valid'] = False
            validation_results['errors'].append(f"File not found: {file_path}")
            return validation_results

        # File size
        max_size = self.intake_config['validation']['max_file_size_mb'] * 1024 * 1024
        if file_path.stat().st_size > max_size:
            validation_results['valid'] = False
            validation_results['errors'].append(
                f"File size exceeds {self.intake_config['validation']['max_file_size_mb']}MB"
            )

        # File extension
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            validation_results['valid'] = False
            validation_results['errors'].append("File must be Excel format (.xlsx)")

        # Duplicate check
        if self.intake_config['validation']['check_duplicates']:
            fingerprint = self._calculate_fingerprint(file_path)
            if fingerprint in self.file_fingerprints.values():
                validation_results['warnings'].append("Duplicate file detected")
            self.file_fingerprints[str(file_path)] = fingerprint

        return validation_results

    def add_bom_file(self, file_path, metadata=None):
        """
        Add a new BOM file to the intake system

        Args:
            file_path: path to BOM file
            metadata: optional dict with customer, location, etc.
        """
        file_path = Path(file_path)

        # Validate
        validation = self._validate_file(file_path)
        if not validation['valid']:
            self.logger.error(f"❌ Validation failed for {file_path.name}")
            for error in validation['errors']:
                self.logger.error(f"   └─ {error}")
            return {'status': 'failed', 'errors': validation['errors']}

        if validation['warnings']:
            for warning in validation['warnings']:
                self.logger.warning(f"⚠️  {warning}")

        # Copy to pending
        dest_path = self.dirs['pending'] / file_path.name
        shutil.copy2(file_path, dest_path)

        # Register file
        self.file_registry[str(dest_path)] = {
            'filename': file_path.name,
            'path': str(dest_path),
            'status': FileStatus.PENDING.value,
            'added_date': datetime.now().isoformat(),
            'metadata': metadata or {},
            'fingerprint': self._calculate_fingerprint(dest_path)
        }

        self.processing_queue.append(str(dest_path))

        self.logger.info(f"✅ Added BOM file: {file_path.name}")

        return {'status': 'added', 'file': file_path.name}

    def start_monitoring(self):
        """Start monitoring BOM_INBOX/pending directory"""
        if self.monitoring:
            self.logger.warning("Monitoring already running")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("🔍 BOM intake monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("⛔ BOM intake monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        check_interval = self.intake_config['monitoring']['check_interval_seconds']

        while self.monitoring:
            try:
                self._check_pending_files()
                self._process_queue()
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

            time.sleep(check_interval)

    def _check_pending_files(self):
        """Check for new files in pending directory"""
        pending_dir = self.dirs['pending']

        for file_path in pending_dir.glob('*.xlsx'):
            if str(file_path) not in self.file_registry:
                # New file detected
                validation = self._validate_file(file_path)

                if validation['valid']:
                    self.file_registry[str(file_path)] = {
                        'filename': file_path.name,
                        'path': str(file_path),
                        'status': FileStatus.PENDING.value,
                        'detected_date': datetime.now().isoformat(),
                        'fingerprint': self._calculate_fingerprint(file_path)
                    }
                    self.processing_queue.append(str(file_path))
                    self.logger.info(f"📄 New file detected: {file_path.name}")
                else:
                    self.logger.error(f"❌ Validation failed: {file_path.name}")

    def _process_queue(self):
        """Process files in queue"""
        max_concurrent = self.intake_config['monitoring']['max_concurrent_files']
        processing_count = sum(1 for f in self.file_registry.values()
                              if f['status'] == FileStatus.PROCESSING.value)

        while self.processing_queue and processing_count < max_concurrent:
            file_path = self.processing_queue.pop(0)
            self._process_file(file_path)
            processing_count += 1

    def _process_file(self, file_path):
        """Process a single BOM file"""
        file_path = Path(file_path)

        try:
            # Update status
            self.file_registry[str(file_path)]['status'] = FileStatus.PROCESSING.value
            self.file_registry[str(file_path)]['processing_start'] = datetime.now().isoformat()

            self.logger.info(f"⚙️  Processing: {file_path.name}")

            # TODO: Call consolidation pipeline
            # result = consolidation_pipeline.process(file_path, self.file_registry[str(file_path)]['metadata'])

            # Simulate processing
            time.sleep(1)

            # Move to completed
            completed_path = self.dirs['completed'] / file_path.name
            shutil.move(str(file_path), str(completed_path))

            # Update registry
            self.file_registry[str(completed_path)] = self.file_registry.pop(str(file_path))
            self.file_registry[str(completed_path)]['status'] = FileStatus.COMPLETED.value
            self.file_registry[str(completed_path)]['path'] = str(completed_path)
            self.file_registry[str(completed_path)]['completed_date'] = datetime.now().isoformat()

            self.logger.info(f"✅ Completed: {file_path.name}")

        except Exception as e:
            self.logger.error(f"❌ Error processing {file_path.name}: {e}")

            # Move to failed
            failed_path = self.dirs['failed'] / file_path.name
            shutil.move(str(file_path), str(failed_path))

            # Update registry
            self.file_registry[str(failed_path)] = self.file_registry.pop(str(file_path))
            self.file_registry[str(failed_path)]['status'] = FileStatus.FAILED.value
            self.file_registry[str(failed_path)]['path'] = str(failed_path)
            self.file_registry[str(failed_path)]['error'] = str(e)

    def list_queue_status(self):
        """Get current queue status"""
        status = {
            'monitoring': self.monitoring,
            'queue_size': len(self.processing_queue),
            'total_files': len(self.file_registry),
            'by_status': defaultdict(list)
        }

        for file_path, file_info in self.file_registry.items():
            status['by_status'][file_info['status']].append({
                'filename': file_info['filename'],
                'added': file_info.get('added_date', file_info.get('detected_date')),
                'path': file_info['path']
            })

        return status

    def print_status(self):
        """Print current system status"""
        status = self.list_queue_status()

        print("\n" + "="*80)
        print("BOM INTAKE SYSTEM - STATUS")
        print("="*80)
        print(f"\n📡 Monitoring: {'🟢 Active' if status['monitoring'] else '🔴 Inactive'}")
        print(f"📋 Queue Size: {status['queue_size']}")
        print(f"📊 Total Files: {status['total_files']}")

        for status_type, files in status['by_status'].items():
            print(f"\n{status_type.upper()} ({len(files)} files):")
            for f in files:
                print(f"   └─ {f['filename']}")

        print("\n" + "="*80 + "\n")


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n🚀 Initializing BOM Intake System...\n")

    intake = BOMIntakeSystem()
    intake.print_status()

    # Test: Add a sample file
    # intake.add_bom_file("sample.xlsx", metadata={"customer": "TEST"})

    print("✅ BOM Intake System ready!")
    print("\nTo start monitoring:")
    print("  intake.start_monitoring()")
    print("\nTo add files:")
    print('  intake.add_bom_file("path/to/file.xlsx", metadata={...})')
