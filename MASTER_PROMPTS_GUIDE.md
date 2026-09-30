# Master Prompts Guide - BOM Consolidation Solution
## Complete Prompts for Rebuilding From Scratch

**Document Version:** 1.0  
**Date:** 2026-09-30  
**Purpose:** Provide all necessary prompts to rebuild this entire project from start  
**Audience:** Developers, AI assistants, project leads

---

## Table of Contents

1. [Meta-Level Project Prompts](#meta-level-project-prompts)
2. [Phase 0 Implementation Prompts](#phase-0-implementation-prompts)
3. [Component-Specific Prompts](#component-specific-prompts)
4. [Testing & Validation Prompts](#testing--validation-prompts)
5. [GitHub & Deployment Prompts](#github--deployment-prompts)
6. [Full Workflow Prompts](#full-workflow-prompts)

---

## Meta-Level Project Prompts

### Overall Project Vision
```
We're building a comprehensive BOM (Bill of Materials) consolidation solution for NVIDIA L11 
networking equipment. The goal is to consolidate data from multiple customers (IREN, Anthropic) 
across different file formats, apply intelligent categorization, and provide analysis tools.

Key Requirements:
- Support multiple BOM file formats (IREN L11, Anthropic PnL)
- Consolidate 14 different files into unified data
- Intelligent item categorization (Cables, Rack, Switch, Transceiver)
- Item mapping and deduplication
- Reference database lookup and enrichment
- Web-based dashboard for visualization
- Intelligent analysis agent

Build in phases:
- Phase 0: Reference management & intake infrastructure (foundation)
- Phase 1: Configuration system for flexible formats
- Phase 2: Dynamic data extraction engine
- Phase 3: Update detection & delta analysis
- Phase 4: Version control & historical tracking
```

### Architecture Overview Prompt
```
Design a flexible, scalable architecture for BOM consolidation that:

1. Is configuration-driven (uses JSON for settings, not hardcoded values)
2. Can add new reference databases without code changes
3. Monitors directories for new BOM files automatically
4. Validates files before processing
5. Detects duplicate files
6. Manages a processing queue
7. Tracks file status (pending → processing → completed/failed)
8. Logs all operations
9. Provides both programmatic and web interfaces

The system should be modular with these layers:
- Configuration Layer (JSON files)
- Reference Management Layer (database lookups)
- File Intake Layer (monitoring and validation)
- Data Processing Layer (consolidation and transformation)
- Output Layer (Excel, HTML dashboard, JSON API)

Use error handling, logging, and comprehensive documentation throughout.
```

---

## Phase 0 Implementation Prompts

### Phase 0 Overall Prompt
```
Implement Phase 0: Reference File Management System & BOM Intake Infrastructure

This is the foundation layer for the BOM consolidation system. Build two systems:

1. REFERENCE FILE MANAGER
   Purpose: Enable dynamic management of reference databases without code changes
   
   Features:
   - Load reference Excel files with flexible column mappings
   - Support multiple sheets per reference file
   - Search for items across references
   - Normalize search keys (remove dashes, spaces, etc.)
   - Track versions with automatic backups
   - Add new references dynamically via API
   - Update existing references with version control
   
   API Methods:
   - __init__(config_file)
   - load_reference(name)
   - add_reference_source(name, file_path, sheets_config, description)
   - update_reference_source(name, file_path, sheets_config)
   - find_item(query, reference_name)
   - list_references()
   - get_reference_stats(name)

2. BOM INTAKE SYSTEM
   Purpose: Automate BOM file intake with validation and processing
   
   Features:
   - Monitor directories for new BOM files
   - Validate files (format, size, metadata)
   - Detect duplicates via file fingerprinting
   - Manage processing queue
   - Track file status (pending/processing/completed/failed)
   - Support concurrent file processing
   - Comprehensive logging to files
   - Archive and cleanup
   
   API Methods:
   - __init__(config_file)
   - add_bom_file(file_path, metadata)
   - start_monitoring()
   - stop_monitoring()
   - _check_pending_files()
   - _process_queue()
   - list_queue_status()

Create JSON configuration files for both systems with sensible defaults.
Include full error handling, logging, and documentation.
```

### Reference Manager Implementation Prompt
```
Create BOM_REFERENCE_MANAGER.py with the ReferenceFileManager class.

Requirements:

1. Configuration Loading
   - Load from JSON config file (reference_sources.json)
   - Define reference databases with sheet mappings
   - Support dynamic loading of references

2. Reference Loading
   - Read Excel files (.xlsx)
   - Parse multiple sheets per reference file
   - Extract columns based on configuration
   - Normalize data (remove dashes, spaces from keys)

3. Search Functionality
   - Find items by normalized query
   - Search across multiple references
   - Return matching items with source information

4. Version Management
   - Track version numbers
   - Create backups on updates
   - Maintain version history
   - Support rollback capability

5. Dynamic Management
   - Add new references without code changes
   - Update existing references with versioning
   - List all available references
   - Get statistics for references

Include:
- Comprehensive logging
- Error handling for missing files/sheets
- Type hints for all methods
- Docstrings for all functions
- Support for multiple sheet configurations

Configuration should define:
- Reference database name and description
- Excel file path
- Sheets to load
- Column mappings per sheet (e.g., {"type": "A", "model_pn": "B", "nvidia_pn": "C", "dell_pn": "E"})
```

### Intake System Implementation Prompt
```
Create BOM_INTAKE_SYSTEM.py with the BOMIntakeSystem class.

Requirements:

1. Directory Management
   - Create directory structure: pending, processing, completed, failed, archive, logs
   - Auto-create directories on initialization
   - Support custom directory paths via configuration

2. File Monitoring
   - Scan pending directory at configurable intervals
   - Detect new .xlsx files
   - Maintain file registry for tracking

3. File Validation
   - Check file exists and is readable
   - Validate Excel format
   - Check file size limits
   - Detect duplicates via SHA256 fingerprinting
   - Validate required metadata

4. Queue Management
   - Maintain processing queue
   - Support configurable concurrent processing
   - Move files through states (pending → processing → completed/failed)
   - Handle processing errors gracefully

5. Status Tracking
   - Track file status with timestamps
   - Record metadata (customer, location, etc.)
   - Store fingerprints for duplicate detection
   - Maintain file registry

6. Logging
   - Log all operations to console and file
   - Create dated log files (YYYYMMDD.log)
   - Include timestamps and log levels
   - Log errors with full context

Configuration should include:
- Directory paths for each state
- Monitoring interval (seconds)
- Max concurrent files
- File patterns to watch
- Validation rules
- File size limits
- Notification settings

Include:
- Threading for background monitoring
- Error recovery
- Comprehensive logging
- Status reporting methods
- File fingerprinting for duplicates
```

### Configuration Files Prompt
```
Create two JSON configuration files:

1. config/reference_sources.json
   Structure:
   {
     "reference_databases": {
       "dell_networking_skus": {
         "name": "Dell Networking Components List",
         "description": "Master reference for Dell networking components",
         "file_path": "Dell Networking components list details WO Pricing.xlsx",
         "enabled": true,
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
     },
     "reference_locations": {
       "directory": "./",
       "backup_directory": "./references/backups/",
       "version_control": true,
       "create_backups": true
     },
     "update_policy": {
       "auto_reload": true,
       "reload_interval_hours": 1,
       "validate_on_load": true,
       "backup_on_update": true,
       "versioning": "enabled"
     }
   }

2. config/intake_config.json
   Structure:
   {
     "intake": {
       "enabled": true,
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
         "require_metadata": true,
         "max_file_size_mb": 100
       },
       "processing": {
         "auto_consolidate": true,
         "create_version": true,
         "generate_delta": true,
         "notify_on_completion": true,
         "generate_report": true
       }
     }
   }
```

### Phase 0 Setup Wrapper Prompt
```
Create PHASE_0_SETUP.py with Phase0System class that:

1. Integrates Reference Manager and Intake System
2. Provides unified interface for Phase 0 operations
3. Includes demonstration and testing capabilities
4. Shows system overview and status
5. Previews future phases

Methods:
- __init__() - Initialize both systems
- print_system_overview() - Display loaded references and queue status
- add_reference() - Add new reference database
- update_reference() - Update existing reference
- find_item() - Search for items
- add_bom_file() - Add file to intake
- start_monitoring() - Start automatic monitoring
- stop_monitoring() - Stop monitoring
- get_queue_status() - Get current queue state
- print_capabilities() - Show Phase 0 features
- get_next_phases_preview() - Preview Phase 1-4

Include demo_phase0() function that:
- Shows capabilities
- Displays system overview
- Demonstrates key features
- Previews upcoming phases
```

---

## Component-Specific Prompts

### For Existing BOM Consolidation
```
We have existing working BOM consolidation code:

BOM_CONSOLIDATION_MERGE.py - Main consolidation pipeline
- Merges IREN and Anthropic BOMs
- Applies item mapping
- Consolidates categories
- Creates Excel output

BOM_CONSOLIDATION_MULTI_FORMAT.py - Multi-format processor
- Handles Anthropic PnL format
- Extracts customer/location metadata

BOM_CONSOLIDATION_FINAL_SOLUTION.py - Core IREN consolidation
- Processes L11 BOM format
- Item categorization logic
- Reference lookups

BOM_AGENT.py - Analysis engine
- Loads consolidated data
- Provides analysis methods
- Generates recommendations

These work together to:
1. Read multiple BOM files
2. Extract and normalize items
3. Look up details in reference database
4. Apply categorization rules
5. Consolidate and deduplicate
6. Generate Excel output with sections
7. Provide analysis and dashboards

Keep these as-is. Phase 0 (Reference Manager + Intake System) will
enhance them by:
- Managing reference databases dynamically
- Automating file intake
- Triggering consolidation automatically
```

---

## Testing & Validation Prompts

### Reference Manager Testing Prompt
```
Create tests for ReferenceFileManager to verify:

1. Configuration Loading
   - Loads reference_sources.json correctly
   - Handles missing config file gracefully
   - Parses all reference definitions

2. Reference Loading
   - Loads Excel files successfully
   - Parses all configured sheets
   - Extracts columns correctly
   - Normalizes keys (removes dashes, spaces)

3. Search Functionality
   - Finds exact matches
   - Returns empty for non-matches
   - Searches across multiple references
   - Returns source information

4. Version Management
   - Tracks versions correctly
   - Creates backups on update
   - Increments version numbers
   - Lists version history

5. Error Handling
   - Handles missing files gracefully
   - Handles missing sheets gracefully
   - Provides helpful error messages
   - Logs errors appropriately

Test with:
- Real reference files
- Missing/empty files
- Malformed JSON configs
- Invalid column references
```

### Intake System Testing Prompt
```
Create tests for BOMIntakeSystem to verify:

1. Directory Management
   - Creates directory structure
   - Handles existing directories
   - Creates logs properly

2. File Validation
   - Accepts valid .xlsx files
   - Rejects non-Excel files
   - Rejects oversized files
   - Detects duplicates
   - Validates metadata

3. Queue Management
   - Adds files to queue
   - Processes files in order
   - Handles concurrent processing
   - Moves files between directories
   - Updates status correctly

4. Monitoring
   - Detects new files
   - Monitors at correct interval
   - Handles monitoring start/stop
   - Maintains file registry

5. Error Handling
   - Handles missing files
   - Handles processing errors
   - Moves failed files to failed directory
   - Logs all errors
   - Recovers gracefully

6. Logging
   - Creates log files
   - Includes timestamps
   - Has appropriate log levels
   - Archives old logs

Test with:
- Sample BOM files
- Duplicate files
- Invalid files
- Network paths
- Large files
```

### Integration Testing Prompt
```
Test Phase 0 system integration:

1. Reference Manager + Intake System
   - Both initialize without errors
   - Can search items from intake files
   - Can configure references dynamically
   - Can monitor and process simultaneously

2. Configuration Loading
   - Both read their configs
   - Can update configs via API
   - Changes persist

3. Error Propagation
   - Errors don't crash system
   - Errors are logged appropriately
   - Recovery is automatic

4. Performance
   - Reference searches are fast (<100ms)
   - File monitoring is responsive
   - Queue processing is efficient
   - Memory usage is reasonable

Run full demo:
python PHASE_0_SETUP.py
```

---

## GitHub & Deployment Prompts

### GitHub Repository Setup Prompt
```
Set up GitHub repository for the BOM Consolidation project:

1. Create Repository
   - Name: L11-BOM-Agent
   - Description: BOM Consolidation Solution with Reference Management & Intake System
   - Visibility: Public or Private (your choice)
   - Initialize with: No template

2. Configure Repository
   - Set main branch as default
   - Enable branch protection:
     - Require pull request reviews
     - Require status checks
     - Dismiss stale reviews

3. Add Documentation
   - README.md (main documentation)
   - PHASE_0_README.md (Phase 0 guide)
   - GITHUB_PUSH_GUIDE.md (deployment guide)

4. Create Branches for Phases
   - main (production)
   - phase-1-configuration-system
   - phase-2-dynamic-extraction
   - phase-3-update-detection
   - phase-4-version-control

5. Configure Issues/Projects
   - Create project for phases
   - Add issue templates
   - Set up milestone tracking
```

### Git Push Prompt
```
Push Phase 0 to GitHub:

1. Initialize local repository
   git init
   git config user.name "Your Name"
   git config user.email "your.email@example.com"

2. Add all files
   git add -A

3. Create initial commit
   git commit -m "Phase 0: Reference Management & BOM Intake Infrastructure"

4. Add remote (choose one)
   
   Option A - HTTPS:
   git remote add origin https://github.com/USERNAME/L11-BOM-Agent.git
   
   Option B - SSH:
   git remote add origin git@github.com:USERNAME/L11-BOM-Agent.git

5. Set main branch
   git branch -M main

6. Push to GitHub
   git push -u origin main

7. Verify
   - Check GitHub for all files
   - Verify commit history
   - Test cloning fresh copy
```

---

## Full Workflow Prompts

### Complete Project Build Prompt
```
Build the complete BOM Consolidation Solution from scratch:

PHASE 0: Foundation (1-2 hours)
1. Create BOM_REFERENCE_MANAGER.py
   - Dynamic reference database management
   - Version control and backups
   - Item search functionality

2. Create BOM_INTAKE_SYSTEM.py
   - File monitoring and validation
   - Queue management
   - Status tracking and logging

3. Create configuration files
   - config/reference_sources.json
   - config/intake_config.json

4. Create PHASE_0_SETUP.py
   - Integration wrapper
   - Demo capabilities

5. Push to GitHub

PHASE 1: Configuration System (2-3 hours)
[To be defined after Phase 0 is complete]

PHASE 2: Dynamic Extraction (3-4 hours)
[To be defined after Phase 1 is complete]

PHASE 3: Update Detection (2-3 hours)
[To be defined after Phase 2 is complete]

PHASE 4: Version Control (2-3 hours)
[To be defined after Phase 3 is complete]

Each phase:
- Review existing work
- Design architecture
- Implement components
- Test thoroughly
- Document
- Commit to GitHub
- Plan next phase
```

### Quick Rebuild Prompt (If Starting Over)
```
To quickly rebuild this project from scratch:

1. Create project structure
   mkdir -p config
   mkdir -p BOM_INBOX/{pending,processing,completed,failed,archive,logs}

2. Create Phase 0 components (use component-specific prompts above):
   - BOM_REFERENCE_MANAGER.py
   - BOM_INTAKE_SYSTEM.py
   - PHASE_0_SETUP.py
   - config/reference_sources.json
   - config/intake_config.json

3. Copy existing consolidation code:
   - BOM_CONSOLIDATION_MERGE.py
   - BOM_CONSOLIDATION_MULTI_FORMAT.py
   - BOM_AGENT.py
   - bom_dashboard.html

4. Create documentation:
   - README.md
   - PHASE_0_README.md
   - ARCHITECTURE_V2_BRAINSTORM.md

5. Initialize Git:
   git init
   git add -A
   git commit -m "Initial commit"

6. Push to GitHub (see GitHub & Deployment section)

7. Plan Phase 1 (after Phase 0 is working)

Estimated time: 4-5 hours total
```

---

## Advanced Prompts

### Extending Phase 0 Prompt
```
To extend Phase 0 with additional features:

1. Email Notifications
   - Modify BOMIntakeSystem to send emails
   - Add email config to intake_config.json
   - Implement notification methods

2. Web Dashboard for Intake System
   - Create HTML interface showing queue status
   - Display file history
   - Show processing logs
   - Real-time updates via WebSocket or polling

3. REST API for Reference Manager
   - Create Flask/FastAPI endpoints
   - Add authentication
   - Implement CRUD operations
   - Add search endpoints

4. Database Backend
   - Replace file-based registry with database
   - Add persistent storage
   - Implement query capabilities
   - Add backup/restore

5. Advanced Monitoring
   - Health checks
   - Performance metrics
   - Error rate tracking
   - Processing time analytics
```

### Phase 1 Implementation Prompt (When Ready)
```
When ready for Phase 1, use this prompt:

"Build Phase 1: Configuration System for flexible BOM format definitions

This phase adds flexibility for handling different BOM formats without code changes.

Create:
1. Format Definitions (JSON)
   - Specify Excel sheets to read
   - Define column names and positions
   - Specify section detection rules
   - Define metadata extraction rules

2. Categorization Rules (JSON)
   - Priority-based categorization
   - Pattern-based rules
   - Reference-based lookups
   - Custom rule support

3. Component Mappings (JSON)
   - Map item names to canonical names
   - Define item categories
   - Specify item consolidation rules

4. Format Processor (Python)
   - Auto-detect format from file structure
   - Extract data using format definitions
   - Apply categorization rules
   - Integrate with Phase 0 systems

This allows:
- Adding new BOM formats without code changes
- Supporting multiple customers/formats
- Flexible categorization
- Dynamic consolidation rules"
```

---

## Troubleshooting Prompts

### If Reference Manager Fails Prompt
```
If ReferenceFileManager has issues:

1. Verify configuration
   - Check reference_sources.json exists
   - Verify file paths are correct
   - Check sheet names match Excel file
   - Verify column letters are correct

2. Check reference files
   - Ensure Excel files exist
   - Verify sheets are present
   - Check data is in expected rows
   - Look for format issues

3. Debug imports
   python -c "from BOM_REFERENCE_MANAGER import ReferenceFileManager; print('OK')"

4. Test loading
   python -c "
   from BOM_REFERENCE_MANAGER import ReferenceFileManager
   mgr = ReferenceFileManager()
   mgr.print_summary()
   "

5. Check logs
   - Review console output
   - Check for error messages
   - Verify configuration loading
```

### If Intake System Fails Prompt
```
If BOMIntakeSystem has issues:

1. Check configuration
   - Verify intake_config.json exists
   - Check all directory paths
   - Verify monitoring settings
   - Check validation rules

2. Check directories
   - Ensure BOM_INBOX structure exists
   - Verify permissions
   - Check disk space

3. Debug startup
   python -c "from BOM_INTAKE_SYSTEM import BOMIntakeSystem; intake = BOMIntakeSystem(); intake.print_status()"

4. Check logs
   - Look in BOM_INBOX/logs/
   - Check for error messages
   - Review timestamps

5. Test file addition
   python -c "
   from BOM_INTAKE_SYSTEM import BOMIntakeSystem
   intake = BOMIntakeSystem()
   intake.add_bom_file('test.xlsx', metadata={'customer': 'TEST'})
   "
```

---

## Quick Reference

### Key Files to Create
```
BOM_REFERENCE_MANAGER.py     - Reference database management
BOM_INTAKE_SYSTEM.py         - BOM file intake automation
PHASE_0_SETUP.py             - Integration wrapper
config/reference_sources.json - Reference configuration
config/intake_config.json     - Intake configuration
.gitignore                   - Git ignore rules
PHASE_0_README.md            - Phase 0 documentation
GITHUB_PUSH_GUIDE.md         - GitHub deployment guide
```

### Key Methods to Implement
```
ReferenceFileManager:
- load_reference(name)
- find_item(query, reference_name)
- add_reference_source(name, file_path, sheets_config)
- update_reference_source(name, file_path, sheets_config)
- list_references()

BOMIntakeSystem:
- add_bom_file(file_path, metadata)
- start_monitoring()
- stop_monitoring()
- list_queue_status()
```

### Key Tests to Run
```
python PHASE_0_SETUP.py  # Full demo
```

---

## Final Notes

**Key Principles:**
1. Configuration-driven (JSON, not hardcoded)
2. Error handling everywhere
3. Comprehensive logging
4. Well-documented code
5. Modular and extensible
6. Phase-based architecture

**Success Criteria:**
- ✅ Phase 0 fully implemented
- ✅ Comprehensive testing
- ✅ All documentation complete
- ✅ GitHub repository set up
- ✅ Code is production-ready
- ✅ Ready for Phase 1

**Timeline:**
- Phase 0: 1-2 hours
- Phases 1-4: 10-15 hours total

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-30  
**Status:** Complete and ready to use
