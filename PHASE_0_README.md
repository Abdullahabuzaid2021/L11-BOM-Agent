# Phase 0: Reference Management & BOM Intake Infrastructure

## Overview

Phase 0 is the foundational layer of the next-generation BOM consolidation system. It provides two critical systems:

1. **Reference File Manager** - Dynamic management of reference databases without code changes
2. **BOM Intake System** - Automated monitoring and processing of new BOM files

These components form the infrastructure foundation for all subsequent phases (1-4).

---

## Component Details

### 1. Reference File Manager (`BOM_REFERENCE_MANAGER.py`)

Manages dynamic reference databases for item lookups and enrichment.

**Key Features:**
- Load and manage multiple reference databases
- Normalize model PNs and search keys
- Version tracking with automatic backups
- Add/update references without code changes
- Cross-reference searching

**Methods:**
```python
from BOM_REFERENCE_MANAGER import ReferenceFileManager

manager = ReferenceFileManager()

# Search for items
result = manager.find_item("920-9N62F-00LI-GC0")

# Add new reference
manager.add_reference_source(
    name="vendor_skus",
    file_path="Vendor Reference.xlsx",
    sheets_config=[{
        "name": "SKU List",
        "columns": {"type": "A", "model_pn": "B", "pn": "C"}
    }],
    description="Vendor SKU reference"
)

# Update existing reference
manager.update_reference_source(
    name="dell_networking_skus",
    file_path="Updated Dell Reference.xlsx"
)

# List all references
refs = manager.list_references()
```

**Configuration:** `config/reference_sources.json`

---

### 2. BOM Intake System (`BOM_INTAKE_SYSTEM.py`)

Automated monitoring and processing of new BOM files.

**Key Features:**
- Directory-based file monitoring
- Automatic file validation
- Duplicate detection via file fingerprinting
- Processing queue management
- File status tracking (pending → processing → completed/failed)
- Detailed logging and error handling

**Methods:**
```python
from BOM_INTAKE_SYSTEM import BOMIntakeSystem

intake = BOMIntakeSystem()

# Add a BOM file manually
intake.add_bom_file(
    "new_bom.xlsx",
    metadata={"customer": "IREN", "location": "Mackenzie"}
)

# Start automatic monitoring
intake.start_monitoring()

# Check queue status
status = intake.list_queue_status()
print(f"Pending: {len(status['by_status']['pending'])}")
print(f"Processing: {len(status['by_status']['processing'])}")
```

**Configuration:** `config/intake_config.json`

**Directory Structure:**
```
BOM_INBOX/
├── pending/       # New files awaiting processing
├── processing/    # Currently being processed
├── completed/     # Successfully processed
├── failed/        # Processing failed
├── archive/       # Archived files
└── logs/          # Processing logs
```

---

## Configuration Files

### `config/reference_sources.json`

Defines available reference databases:
```json
{
  "reference_databases": {
    "dell_networking_skus": {
      "name": "Dell Networking Components List",
      "file_path": "Dell Networking components list details WO Pricing.xlsx",
      "sheets": [
        {
          "name": "Enigma Prime SKU",
          "columns": {
            "type": "A",
            "model_pn": "B",
            "nvidia_pn": "C",
            "dell_pn": "E"
          }
        }
      ]
    }
  }
}
```

### `config/intake_config.json`

Configures intake system behavior:
```json
{
  "intake": {
    "directories": {
      "input_directory": "BOM_INBOX/pending/",
      "processing_directory": "BOM_INBOX/processing/",
      "completed_directory": "BOM_INBOX/completed/",
      "failed_directory": "BOM_INBOX/failed/",
      "archive_directory": "BOM_INBOX/archive/",
      "log_directory": "BOM_INBOX/logs/"
    },
    "monitoring": {
      "enabled": true,
      "check_interval_seconds": 300,
      "max_concurrent_files": 3,
      "file_pattern": "*.xlsx"
    },
    "validation": {
      "check_format": true,
      "check_duplicates": true,
      "check_fingerprint": true,
      "max_file_size_mb": 100
    }
  }
}
```

---

## Quick Start

### 1. Initialize Phase 0 System

```python
from PHASE_0_SETUP import Phase0System

phase0 = Phase0System()
```

### 2. Search Reference Databases

```python
# Find an item
result = phase0.find_item("920-9N62F-00LI-GC0")
print(f"Found: {result['found']}")
print(f"Matches: {result['count']}")
```

### 3. Add New Reference

```python
phase0.add_reference(
    "vendor_x_skus",
    "VendorX_Reference.xlsx",
    [{
        "name": "Master Catalog",
        "columns": {"type": "A", "model": "B", "pn": "C"}
    }],
    "Vendor X SKU reference"
)
```

### 4. Monitor BOM Intake

```python
# Start monitoring
phase0.start_monitoring()

# Add files manually
phase0.add_bom_file(
    "bom_file.xlsx",
    metadata={"customer": "ABC", "location": "XYZ"}
)

# Check status
status = phase0.get_queue_status()
```

---

## Architecture Flow

```
┌─────────────────────────────────────────┐
│   PHASE 0: FOUNDATION LAYER             │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Reference File Manager          │  │
│  │  ├─ Load references              │  │
│  │  ├─ Search items                 │  │
│  │  ├─ Version tracking             │  │
│  │  └─ Add/update databases         │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  BOM Intake System               │  │
│  │  ├─ Monitor directories          │  │
│  │  ├─ Validate files               │  │
│  │  ├─ Detect duplicates            │  │
│  │  ├─ Manage queue                 │  │
│  │  └─ Track status                 │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
         ↓
    [Future Phases]
    Phase 1: Configuration System
    Phase 2: Dynamic Data Extraction
    Phase 3: Update Detection
    Phase 4: Version Control
```

---

## Transitioning to Phase 1

Phase 0 sets the stage for Phase 1 (Configuration System), which will:

- Define flexible BOM format specifications
- Create dynamic component mapping rules
- Implement category classification rules
- Enable zero-code format additions

**Phase 0 enables Phase 1 by providing:**
- Reliable reference database management
- Stable file intake pipeline
- Core infrastructure for processing

---

## File Manifest

| File | Purpose |
|------|---------|
| `BOM_REFERENCE_MANAGER.py` | Dynamic reference database management |
| `BOM_INTAKE_SYSTEM.py` | Automated BOM file monitoring and processing |
| `PHASE_0_SETUP.py` | Integration wrapper and phase initialization |
| `config/reference_sources.json` | Reference database configuration |
| `config/intake_config.json` | Intake system configuration |
| `PHASE_0_README.md` | This documentation |

---

## Next Steps

1. ✅ **Phase 0 Complete** - Reference management and intake infrastructure ready
2. 🔄 **Phase 1 (Next)** - Configuration system for flexible format definitions
3. ⏳ **Phase 2** - Dynamic data extraction engine
4. ⏳ **Phase 3** - Update detection and delta analysis
5. ⏳ **Phase 4** - Version control and historical tracking

---

## Error Handling

Both systems include comprehensive error handling:

- **Reference Manager:** Validates file existence, tracks versions, creates backups
- **Intake System:** Validates file format/size, detects duplicates, logs all operations

All errors are logged to `BOM_INBOX/logs/` for debugging.

---

**Version:** 1.0  
**Status:** ✅ Ready for production  
**Last Updated:** 2026-09-30
