# BOM Solution - Next Level Architecture Brainstorm

## 🎯 Goals
1. **Flexible Format Recognition** - Auto-detect and adapt to new BOM formats
2. **Dynamic Configuration** - Add/update components without code changes
3. **Update Detection** - Recognize new vs updated BOMs automatically
4. **Version Control** - Track BOMs over time with delta comparison

---

## 🏗️ Architecture Design

### Level 1: Configuration-Driven System

```
CONFIG LAYER (JSON/YAML)
├── format_definitions.json      # Define BOM file formats
├── categorization_rules.json    # Define item categories
├── component_mappings.json      # Define item equivalences
├── section_patterns.json        # Define section detection
└── customer_locations.json      # Define customer/location extraction

REFERENCE MANAGEMENT LAYER (NEW)
├── reference_sources.json       # Define reference file locations
├── ReferenceFileManager         # Load/update reference data
├── ReferenceVersionControl      # Version reference files
└── ReferenceValidator           # Validate reference data integrity

INTAKE & PROCESSING LAYER (NEW)
├── BOM_INBOX/                   # Directory for new BOM files
│   ├── pending/                 # New files awaiting processing
│   ├── processing/              # Currently being processed
│   ├── completed/               # Successfully processed
│   └── failed/                  # Failed processing attempts
├── IntakeMonitor                # Watch for new BOMs
├── FileValidator                # Validate BOM structure
└── ProcessingQueue              # Queue management

PROCESSING LAYER
├── FormatDetector              # Auto-detect BOM format
├── SheetAnalyzer               # Analyze sheet structure dynamically
├── DataExtractor               # Extract data based on config
├── Normalizer                  # Normalize items across formats
└── Validator                   # Validate data quality

PERSISTENCE LAYER
├── BOMRepository               # Version-controlled storage
├── ChangeTracker               # Track changes between versions
├── DeltaCalculator             # Calculate deltas
└── TimeSeriesDB                # Historical data storage
```

### Level 2: Format Recognition System

**Instead of hardcoded formats, use configuration:**

```json
// format_definitions.json
{
  "formats": {
    "IREN_L11": {
      "name": "IREN L11 BOM Format",
      "file_pattern": "BOM - NETWORK - *.xlsx",
      "sheets": [
        {
          "name_pattern": "L11 BOM.*",
          "type": "data_sheet",
          "headers": {
            "section": {"column": "A", "pattern": ".*racks.*|.*pdus.*"},
            "model_pn": {"column": "B", "pattern": "920-.*|IR.*"},
            "nvidia_pn": {"column": "C"},
            "dell_pn": {"column": "D"},
            "quantity": {"column": "E", "type": "number"}
          }
        }
      ],
      "metadata": {
        "customer": {"extraction": "filename", "pattern": "IREN|Anthropic"},
        "location": {"extraction": "filename", "pattern": "Mackenzie|Sydney|.*"}
      }
    },
    "ANTHROPIC_PNL": {
      "name": "Anthropic PnL Format",
      "file_pattern": "PNL-NETWORK BOM-*.xlsx",
      "sheets": [
        {
          "name_pattern": "PnL.*",
          "type": "data_sheet",
          "headers": {
            "section": {"column": "B", "pattern": "Networking|RoCE"},
            "model_name": {"column": "C"},
            "nvidia_pn": {"column": "D"},
            "quantity": {"column": "F", "type": "number"}
          }
        }
      ]
    },
    "FUTURE_FORMAT": {
      "name": "Any Future Format",
      "file_pattern": "*.xlsx",
      "auto_detect": true
    }
  }
}
```

### Level 2.5: Reference File Management (NEW!)

**Problem:** Current system hardcodes Dell Networking components list reference file

**Solution: Dynamic Reference Management**

```json
// reference_sources.json
{
  "reference_databases": {
    "dell_networking_skus": {
      "name": "Dell Networking Components List",
      "file_path": "references/Dell Networking components list details WO Pricing.xlsx",
      "sheets": [
        {
          "name": "Enigma Prime SKU",
          "columns": {
            "model_pn": "B",
            "nvidia_pn": "C",
            "dell_pn": "E",
            "type": "A"
          },
          "version": "1.0",
          "last_updated": "2026-09-29"
        },
        {
          "name": "Dell Networking SKU",
          "columns": {
            "model_pn": "B",
            "nvidia_pn": "C",
            "dell_pn": "G",
            "type": "A"
          },
          "version": "1.0",
          "last_updated": "2026-09-29"
        }
      ]
    },
    "future_reference_database": {
      "name": "Placeholder for new reference source",
      "file_path": "references/future_reference.xlsx",
      "enabled": false,
      "sheets": []
    }
  },
  
  "reference_locations": {
    "directory": "references/",
    "backup_directory": "references/backups/",
    "version_control": true
  },
  
  "update_policy": {
    "auto_reload": true,
    "reload_interval_hours": 1,
    "validate_on_load": true,
    "backup_on_update": true,
    "versioning": "enabled"
  }
}
```

**Reference File Manager Class:**

```python
class ReferenceFileManager:
    def __init__(self, config_file):
        """Initialize with reference configuration"""
        self.config = load_config(config_file)
        self.references = {}
        self.version_history = {}
        self.last_loaded = {}
    
    def add_reference_source(self, name, file_path, sheets_config):
        """
        Add a new reference database dynamically
        - name: identifier for this reference
        - file_path: location of reference file
        - sheets_config: definition of sheets and columns
        """
        self.config['reference_databases'][name] = {
            'file_path': file_path,
            'sheets': sheets_config,
            'version': '1.0',
            'added_date': datetime.now().isoformat()
        }
        self.load_reference(name)
        self.save_config()
    
    def update_reference_source(self, name, file_path=None, sheets_config=None):
        """
        Update an existing reference database
        - Backs up old version
        - Loads new version
        - Tracks version history
        """
        if name not in self.config['reference_databases']:
            raise ValueError(f"Reference {name} not found")
        
        # Backup current version
        old_config = copy.deepcopy(self.config['reference_databases'][name])
        backup_path = self._create_backup(name, old_config)
        
        # Update configuration
        if file_path:
            self.config['reference_databases'][name]['file_path'] = file_path
        if sheets_config:
            self.config['reference_databases'][name]['sheets'] = sheets_config
        
        # Version tracking
        old_version = self.config['reference_databases'][name].get('version', '1.0')
        new_version = self._increment_version(old_version)
        self.config['reference_databases'][name]['version'] = new_version
        self.config['reference_databases'][name]['last_updated'] = datetime.now().isoformat()
        
        # Reload
        self.load_reference(name)
        self.save_config()
        
        return {
            'status': 'updated',
            'name': name,
            'old_version': old_version,
            'new_version': new_version,
            'backup_path': backup_path
        }
    
    def load_reference(self, name):
        """Load reference data into memory"""
        ref_config = self.config['reference_databases'][name]
        file_path = ref_config['file_path']
        
        # Load Excel file
        wb = openpyxl.load_workbook(file_path)
        
        self.references[name] = {
            'config': ref_config,
            'data': {},
            'loaded_at': datetime.now().isoformat()
        }
        
        for sheet_config in ref_config['sheets']:
            sheet_name = sheet_config['name']
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                self.references[name]['data'][sheet_name] = self._parse_sheet(
                    ws, sheet_config['columns']
                )
    
    def list_references(self):
        """List all available reference sources"""
        return {
            name: {
                'file': config['file_path'],
                'version': config.get('version', '1.0'),
                'sheets': [s['name'] for s in config['sheets']],
                'status': 'loaded' if name in self.references else 'not_loaded'
            }
            for name, config in self.config['reference_databases'].items()
        }
    
    def get_reference(self, name, sheet_name, query):
        """Query a reference database"""
        if name not in self.references:
            self.load_reference(name)
        
        return self.references[name]['data'].get(sheet_name, [])
```

### Level 3: BOM Intake System (NEW!)

**Problem:** BOMs currently need to be in specific directory; manual processing

**Solution: Automated BOM Intake Pipeline**

```
BOM_INBOX/
├── pending/
│   ├── BOM - NETWORK - 2026-10-01 - IREN - NEW.xlsx
│   └── PNL-NETWORK BOM-2026-10-01-Anthropic-UK.xlsx
├── processing/
│   └── [file currently being processed]
├── completed/
│   ├── 2026-09-29/
│   │   ├── BOM - NETWORK - 2026-08-24- IREN - ...xlsx (processed)
│   │   └── processing.log
│   └── 2026-09-30/
├── failed/
│   ├── BOM - INVALID.xlsx (reason: invalid_format)
│   └── error_log.json
└── queue.json
```

**Intake Configuration:**

```json
// intake_config.json
{
  "intake": {
    "enabled": true,
    "input_directory": "BOM_INBOX/pending/",
    "processing_directory": "BOM_INBOX/processing/",
    "completed_directory": "BOM_INBOX/completed/",
    "failed_directory": "BOM_INBOX/failed/",
    "archive_directory": "BOM_INBOX/archive/",
    "log_directory": "BOM_INBOX/logs/",
    
    "monitoring": {
      "enabled": true,
      "check_interval_seconds": 300,
      "max_concurrent": 3
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
      "notify_on_completion": true
    },
    
    "notifications": {
      "email_on_success": ["admin@company.com"],
      "email_on_failure": ["admin@company.com"],
      "slack_on_completion": true
    }
  }
}
```

**Intake Monitor & Processor:**

```python
class BOMIntakeSystem:
    def __init__(self, config_file):
        self.config = load_config(config_file)
        self.queue = ProcessingQueue()
        self.validator = FileValidator()
        self.processor = BOMProcessor()
        self.logger = set_up_logging(self.config['intake']['log_directory'])
    
    def start_monitoring(self):
        """Start watching inbox for new BOMs"""
        while True:
            self._check_pending_files()
            self._process_queue()
            time.sleep(self.config['intake']['monitoring']['check_interval_seconds'])
    
    def _check_pending_files(self):
        """Look for new files in pending directory"""
        pending_dir = Path(self.config['intake']['input_directory'])
        
        for file_path in pending_dir.glob('*.xlsx'):
            try:
                # Validate file
                validation_result = self.validator.validate(file_path)
                
                if not validation_result['valid']:
                    self._move_file(file_path, 'failed', validation_result['error'])
                    continue
                
                # Check for duplicates
                if self._is_duplicate(file_path):
                    self._move_file(file_path, 'failed', 'duplicate_detected')
                    continue
                
                # Add to queue
                self.queue.add(file_path)
                self.logger.info(f"Added to queue: {file_path.name}")
                
            except Exception as e:
                self._move_file(file_path, 'failed', str(e))
                self.logger.error(f"Error processing {file_path.name}: {e}")
    
    def _process_queue(self):
        """Process files in queue"""
        while self.queue.has_items() and self.queue.concurrent_count < self.config['intake']['monitoring']['max_concurrent']:
            file_path = self.queue.next()
            
            try:
                self._move_file(file_path, 'processing')
                
                # Process the BOM
                result = self.processor.process(file_path)
                
                # Create version
                if self.config['intake']['processing']['create_version']:
                    self._create_version(file_path, result)
                
                # Generate delta
                if self.config['intake']['processing']['generate_delta']:
                    delta = self._generate_delta(result)
                
                # Move to completed
                self._move_file(file_path, 'completed')
                
                # Notify
                if self.config['intake']['processing']['notify_on_completion']:
                    self._notify('success', file_path, result)
                
                self.logger.info(f"Successfully processed: {file_path.name}")
                
            except Exception as e:
                self._move_file(file_path, 'failed', str(e))
                self._notify('failure', file_path, str(e))
                self.logger.error(f"Failed processing {file_path.name}: {e}")
    
    def _move_file(self, file_path, destination, reason=None):
        """Move file to appropriate directory"""
        dest_path = Path(self.config['intake'][f'{destination}_directory'])
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory by date if completed
        if destination == 'completed':
            dest_path = dest_path / datetime.now().strftime('%Y-%m-%d')
            dest_path.mkdir(parents=True, exist_ok=True)
        
        new_path = dest_path / file_path.name
        shutil.move(str(file_path), str(new_path))
        
        # Log reason
        if reason:
            log_file = dest_path / 'processing.log'
            with open(log_file, 'a') as f:
                f.write(f"{file_path.name}: {reason}\n")
    
    def _is_duplicate(self, file_path):
        """Check if file is duplicate of processed BOM"""
        fingerprint = self._get_fingerprint(file_path)
        return fingerprint in self.processor.processed_fingerprints
    
    def list_intake_status(self):
        """Get current status of intake system"""
        return {
            'pending': len(list(Path(self.config['intake']['input_directory']).glob('*.xlsx'))),
            'processing': len(list(Path(self.config['intake']['processing_directory']).glob('*.xlsx'))),
            'completed': len(list(Path(self.config['intake']['completed_directory']).rglob('*.xlsx'))),
            'failed': len(list(Path(self.config['intake']['failed_directory']).glob('*.xlsx'))),
            'queue_size': self.queue.size(),
            'queue_position': self.queue.position()
        }
```

### Level 3 (Original): Component Management

```json
// component_mappings.json
{
  "item_equivalences": {
    "IR9148": {
      "names": ["IR9148", "Network rack (DLC)", "IR9148-*"],
      "category": "Rack",
      "type": "infrastructure",
      "specifications": {
        "rack_height": "48U",
        "cooling": "liquid_cooled",
        "power": "redundant"
      },
      "aliases": [
        {"source_format": "anthropic", "name": "Network rack (DLC)"},
        {"source_format": "iren", "name": "IR9148"}
      ]
    },
    "IR9048": {
      "names": ["IR9048", "Network rack (AC)", "IR9048-*"],
      "category": "Rack",
      "type": "infrastructure",
      "specifications": {
        "rack_height": "48U",
        "cooling": "air_cooled",
        "power": "redundant"
      }
    },
    "980-9IAJ0-00XM00": {
      "names": ["980-9IAJ0-00XM00", "NVIDIA Twin Port Transceiver"],
      "category": "Transceiver",
      "type": "networking",
      "specifications": {
        "ports": 2,
        "speed": "400Gbps",
        "form_factor": "OSFP"
      }
    }
  },
  
  "categorization_rules": {
    "priority_order": [
      "hardcoded_rules",
      "reference_database",
      "pattern_matching",
      "keyword_matching",
      "default"
    ],
    "rules": {
      "hardcoded": [
        {"pattern": "Network rack.*DLC", "category": "Rack"},
        {"pattern": "Network rack.*AC", "category": "Rack"},
        {"pattern": "980-.*", "category": "Transceiver"},
        {"pattern": "920-9N110.*", "category": "Switch"}
      ],
      "patterns": [
        {"keywords": ["transceiver", "xcvr", "sfp", "qsfp"], "category": "Transceiver"},
        {"keywords": ["fiber", "cable", "jumper"], "category": "Cables"},
        {"keywords": ["rack", "chassis", "frame"], "category": "Rack"},
        {"keywords": ["switch", "router"], "category": "Switch"}
      ]
    }
  }
}
```

### Level 4: Change Detection & Versioning

```
CHANGE DETECTION ENGINE
├── FileFingerprinter          # SHA256/MD5 of file content
├── UpdateDetector             # Detect if BOM is new vs update
├── DuplicateDetector          # Find duplicate BOMs
└── ChangeComparator           # Compare with previous versions

VERSION MANAGEMENT
├── BOMVersionStore            # Store versioned BOMs
│   ├── v1.0 (2026-09-29)
│   ├── v1.1 (2026-09-30)
│   └── v1.2 (2026-10-01)
├── ChangeLog                  # Track what changed
└── DeltaAnalysis              # Item additions/removals/changes
```

**Change Detection Strategy:**

```python
# Pseudo-code
class BOMChangeDetector:
    def detect_update(self, new_bom, existing_boms):
        """
        Returns:
        - NEW: Completely new BOM from different customer/location
        - UPDATE: Updated version of existing BOM (same source, new data)
        - DUPLICATE: Identical or nearly identical to existing
        - MERGED: Combination of existing BOMs
        """
        fingerprint = hash(new_bom.content)
        
        for existing in existing_boms:
            similarity = calculate_similarity(new_bom, existing)
            
            if similarity > 0.95:
                if fingerprint == existing.fingerprint:
                    return "DUPLICATE"
                else:
                    return "UPDATE"
            elif similarity > 0.7:
                return "MERGED"
        
        return "NEW"
```

### Level 5: Time-Series Version Control

```
VERSION TIMELINE
├── 2026-09-29
│   └── BOM_CONSOLIDATED_v1.0.json
│       ├── metadata
│       ├── items (52 items, 1.9M qty)
│       └── file_sources (9 IREN, 0 Anthropic)
│
├── 2026-09-30
│   └── BOM_CONSOLIDATED_v1.1.json
│       ├── metadata
│       ├── items (52 items, 1.9M qty)  [SAME]
│       └── file_sources (9 IREN, 5 Anthropic) [ADDED]
│
└── 2026-10-01
    └── BOM_CONSOLIDATED_v1.2.json
        ├── metadata
        ├── items (54 items, 2.1M qty)   [DELTA: +2 items, +200K qty]
        └── file_sources (9 IREN, 5 Anthropic, 1 New)

DELTA ANALYSIS (v1.1 → v1.2)
├── Added Items
│   ├── New Item A: 50K qty
│   └── New Item B: 150K qty
├── Removed Items: None
├── Modified Items
│   ├── 980-9IAJ0-00XM00: 1.37M → 1.42M (+50K)
│   └── Transceiver Category: 1.43M → 1.48M (+50K)
└── Impact Analysis
    ├── Cost Delta: +$X million
    ├── Schedule Impact: +2 weeks
    └── Resource Changes: +2 teams needed
```

---

## 🔄 Proposed Implementation Strategy

### Phase 0: Reference & Intake Infrastructure (Week 0 - Foundation)
```
Tasks:
1. Create reference_sources.json configuration
2. Create intake_config.json configuration
3. Build ReferenceFileManager class
   - add_reference_source()
   - update_reference_source()
   - load_reference()
   - list_references()
4. Build BOMIntakeSystem class
   - start_monitoring()
   - validate files
   - manage queue
   - handle processing
5. Create BOM_INBOX directory structure
   - pending/, processing/, completed/, failed/, archive/

Deliverable: 
- Reference files can be added/updated without code changes
- New BOMs are automatically detected and queued
- Complete audit trail of all processing
```

### Phase 1: Configuration System (Week 1)
```
Tasks:
1. Create format_definitions.json
2. Create component_mappings.json
3. Create categorization_rules.json
4. Build FormatDetector class
5. Build ConfigurationManager class

Deliverable: 
- ConfigurationManager can load and validate all configs
- FormatDetector can auto-identify format type
```

### Phase 2: Flexible Data Extraction (Week 2)
```
Tasks:
1. Build DynamicSheetAnalyzer
2. Build DataExtractor (config-driven)
3. Build Normalizer (format-agnostic)
4. Build Validator (config-based validation)
5. Integrate with IntakeSystem

Deliverable:
- Can process new formats without code changes
- Can add new sections/categories via config
- Works with intake system for automatic processing
```

### Phase 3: Update Detection (Week 3)
```
Tasks:
1. Build FileFingerprinter
2. Build UpdateDetector
3. Build DuplicateDetector (integrated with IntakeSystem)
4. Build UpdateLogger
5. Create decision tree for handling updates

Deliverable:
- Auto-detects NEW vs UPDATE vs DUPLICATE BOMs
- Prevents duplicate processing
- IntakeSystem rejects duplicates automatically
```

### Phase 4: Version Control (Week 4)
```
Tasks:
1. Build BOMVersionStore (JSON-based initially)
2. Build ChangeLog system
3. Build DeltaCalculator
4. Build TimeSeriesAnalyzer
5. Build VersionComparator API

Deliverable:
- Complete version history
- Delta analysis between versions
- Trend analysis over time
```

---

## 📊 Data Model - Versioned BOM

```json
{
  "version": "1.2",
  "timestamp": "2026-10-01T14:30:00Z",
  "metadata": {
    "created_date": "2026-09-29T00:00:00Z",
    "last_updated": "2026-10-01T14:30:00Z",
    "format_version": "2.0",
    "change_type": "UPDATE"
  },
  
  "sources": {
    "files": [
      {
        "name": "BOM - NETWORK - 2026-08-24- IREN - 512 Racks.xlsx",
        "format": "IREN_L11",
        "customer": "IREN",
        "location": "Mackenzie, BC",
        "fingerprint": "sha256_hash",
        "processed_date": "2026-09-29"
      }
    ],
    "total_files": 15,
    "new_files_this_version": ["file_name_15"]
  },
  
  "items": [
    {
      "id": "unique_item_id",
      "model_pn": "920-9N62F-00LI-GC1",
      "nvidia_pn": "920-9N62F-00LI-GC1",
      "dell_pn": "3KF5K",
      "name": "SN6600-LD Switch",
      "category": "Switch",
      "section": "Scale out Networking",
      "quantity": {
        "total": 1240,
        "version_added": "1.0",
        "last_updated": "1.2",
        "change_history": [
          {"version": "1.0", "qty": 1200},
          {"version": "1.1", "qty": 1200},
          {"version": "1.2", "qty": 1240}
        ]
      },
      "file_breakdown": {
        "IREN-Mackenzie": 100,
        "IREN-Toronto": 200,
        "Anthropic-Sydney": 50
      },
      "status": "MODIFIED"  // NEW, UNCHANGED, MODIFIED, REMOVED
    }
  ],
  
  "summary": {
    "total_items": 54,
    "total_quantity": 2100000,
    "categories": {
      "Transceiver": {"items": 14, "quantity": 1500000},
      "Cables": {"items": 16, "quantity": 120000},
      "Rack": {"items": 12, "quantity": 380000},
      "Switch": {"items": 12, "quantity": 100000}
    }
  },
  
  "delta": {
    "vs_previous": "1.1",
    "added_items": 2,
    "removed_items": 0,
    "modified_items": 3,
    "quantity_delta": "+200000",
    "cost_delta_estimated": "+$5.2M",
    "timeline_impact": "+3 weeks"
  }
}
```

---

## 🎯 Benefits of This Approach

| Aspect | Current | Next Level |
|--------|---------|-----------|
| **Format Support** | 2 hardcoded formats | Unlimited via config |
| **Adding Components** | Code changes required | Config update only |
| **Reference Updates** | Manual file replacement | Dynamic management API |
| **BOM Intake** | Manual file placement | Automated monitoring + queue |
| **Processing Speed** | Full reprocessing | Incremental updates |
| **Version History** | None | Complete timeline |
| **Delta Analysis** | Manual comparison | Automated |
| **Scalability** | Limited to known formats | Any format possible |
| **Duplicate Detection** | Manual check | Automatic fingerprinting |
| **Error Handling** | Manual restart | Auto retry + logging |
| **Maintenance** | High (code changes) | Low (config changes) |
| **Audit Trail** | None | Complete processing logs |

---

---

## 🔄 Complete System Flow (Next Level)

```
EXTERNAL SOURCES
├── New IREN BOMs
├── New Anthropic BOMs
└── Other customer BOMs (future)
          ↓
BOM_INBOX/pending/
          ↓
IntakeMonitor (monitors every 5 min)
          ↓
┌─────────────────────────────────────────┐
│ FILE VALIDATION                         │
├─────────────────────────────────────────┤
│ ✓ Format check                         │
│ ✓ Structure validation                 │
│ ✓ Fingerprint check (duplicates)       │
│ ✓ Metadata extraction                  │
└─────────────────────────────────────────┘
          ↓
    DUPLICATE? ──YES──→ BOM_INBOX/failed/
          │ NO
          ↓
  ADD TO QUEUE
          ↓
BOMIntakeSystem (max 3 concurrent)
          ↓
┌─────────────────────────────────────────┐
│ FORMAT DETECTION & DATA EXTRACTION      │
├─────────────────────────────────────────┤
│ 1. FormatDetector (config-driven)      │
│ 2. DynamicSheetAnalyzer                │
│ 3. DataExtractor (column mapping)      │
│ 4. Normalizer (across formats)         │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│ REFERENCE LOOKUP & ENRICHMENT           │
├─────────────────────────────────────────┤
│ 1. Load reference (dynamically!)       │
│    - Dell Networking SKU               │
│    - Enigma Prime SKU                  │
│    - Any other reference added         │
│ 2. Match items to reference            │
│ 3. Enrich with NVIDIA/Dell PNs         │
│ 4. Apply categorization rules          │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│ CONSOLIDATION & VERSIONING              │
├─────────────────────────────────────────┤
│ 1. Consolidate with existing BOMs      │
│ 2. Apply item mappings (config)        │
│ 3. Detect NEW vs UPDATE                │
│ 4. Create version (v1.x)               │
│ 5. Calculate delta from v(x-1)         │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│ PERSISTENCE & STORAGE                   │
├─────────────────────────────────────────┤
│ 1. Save versioned JSON                 │
│ 2. Update Excel master file            │
│ 3. Create changelog                    │
│ 4. Archive old versions                │
└─────────────────────────────────────────┘
          ↓
    SUCCESS? ──NO──→ BOM_INBOX/failed/
          │ YES
          ↓
BOM_INBOX/completed/{date}/
          ↓
┌─────────────────────────────────────────┐
│ NOTIFICATIONS & REPORTS                 │
├─────────────────────────────────────────┤
│ ✓ Email notification (admin)           │
│ ✓ Slack notification                   │
│ ✓ Processing log written               │
│ ✓ Delta report generated               │
└─────────────────────────────────────────┘
          ↓
READY FOR ANALYSIS & DASHBOARD
```

---

## 📋 Configuration Files to Create

```
config/
├── format_definitions.json       # NEW: Flexible format support
├── reference_sources.json        # NEW: Reference file management
├── intake_config.json            # NEW: BOM intake system
├── categorization_rules.json
├── component_mappings.json
└── customer_locations.json
```

**New Directories to Create:**

```
BOM_INBOX/
├── pending/                      # New BOMs waiting to be processed
├── processing/                   # BOMs currently being processed
├── completed/
│   ├── 2026-10-01/
│   │   ├── processed_bom.xlsx
│   │   └── processing.log
├── failed/                       # BOMs that failed validation/processing
│   ├── BOM - INVALID.xlsx
│   └── error_log.json
├── archive/                      # Old BOMs (can be deleted after backup)
└── logs/                         # Processing logs and reports
    ├── 2026-10-01.log
    └── intake_status.json

references/
├── Dell Networking components list details WO Pricing.xlsx  (current)
├── Enigma Prime SKU (tracking version history)
├── backups/
│   ├── 2026-09-29/
│   └── 2026-09-30/
└── version_history.json          # Tracks all reference file updates

versions/
├── v1.0.json                     # Initial consolidation
├── v1.1.json                     # After adding Anthropic BOMs
├── v1.2.json                     # After new BOMs added
└── changelog.json                # Track all version changes
```

---

## 🚀 Next Steps

**Key Decisions for You:**

1. **Config Format?** 
   - ✓ JSON (simpler, standard)
   - ○ YAML (more readable)

2. **Version Storage?** 
   - ✓ JSON files (simple, portable)
   - ○ SQLite (more structured)
   - ○ PostgreSQL (scalable)

3. **Intake Processing?** 
   - ✓ Daemon/Service (continuous monitoring)
   - ○ Scheduled batch (daily/weekly)
   - ○ Manual trigger (on-demand)

4. **Start with:**
   - ✓ Phase 0 (Reference + Intake) - Foundation for everything else
   - Then Phase 1-4 progressively

---

**Ready to implement Phase 0 first?** ✅

This will give us:
- Dynamic reference file management
- Automated BOM intake system
- Complete audit trail
- Foundation for all other phases
