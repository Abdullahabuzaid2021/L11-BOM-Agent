"""
PHASE 0 SETUP - Initialize Reference Management & BOM Intake Infrastructure
Sets up the foundation for flexible, scalable BOM processing
"""

import sys
from pathlib import Path

# Import Phase 0 components
from BOM_REFERENCE_MANAGER import ReferenceFileManager
from BOM_INTAKE_SYSTEM import BOMIntakeSystem


class Phase0System:
    """
    Phase 0: Reference Management + BOM Intake Infrastructure
    Foundation for all subsequent phases
    """

    def __init__(self):
        """Initialize Phase 0 system"""
        print("\n" + "="*80)
        print("PHASE 0: REFERENCE MANAGEMENT + BOM INTAKE INFRASTRUCTURE")
        print("="*80)

        # Initialize components
        self.reference_manager = ReferenceFileManager()
        self.intake_system = BOMIntakeSystem()

        print("\n✅ Phase 0 System Initialized!")

    def print_system_overview(self):
        """Print comprehensive system overview"""
        print("\n" + "="*80)
        print("PHASE 0 SYSTEM OVERVIEW")
        print("="*80)

        # Reference Manager
        print("\n📚 REFERENCE MANAGER")
        print("-" * 80)
        print("Manages dynamic reference databases for item lookups")
        self.reference_manager.print_summary()

        # Intake System
        print("\n🚀 BOM INTAKE SYSTEM")
        print("-" * 80)
        print("Automated monitoring and processing of new BOM files")
        self.intake_system.print_status()

    def add_reference(self, name, file_path, sheets_config, description=""):
        """
        Add a new reference database

        Example:
        ```
        phase0.add_reference(
            "vendor_skus",
            "Vendor Reference.xlsx",
            [{"name": "SKU List", "columns": {"model": "A", "pn": "B"}}],
            "Additional vendor SKU reference"
        )
        ```
        """
        return self.reference_manager.add_reference_source(name, file_path, sheets_config, description)

    def update_reference(self, name, file_path=None, sheets_config=None):
        """Update an existing reference database"""
        return self.reference_manager.update_reference_source(name, file_path, sheets_config)

    def find_item(self, query, reference=None):
        """Search for an item in reference databases"""
        return self.reference_manager.find_item(query, reference)

    def add_bom_file(self, file_path, metadata=None):
        """Add a new BOM file for processing"""
        return self.intake_system.add_bom_file(file_path, metadata)

    def start_monitoring(self):
        """Start automatic BOM intake monitoring"""
        return self.intake_system.start_monitoring()

    def stop_monitoring(self):
        """Stop automatic BOM intake monitoring"""
        return self.intake_system.stop_monitoring()

    def get_queue_status(self):
        """Get current processing queue status"""
        return self.intake_system.list_queue_status()

    def print_capabilities(self):
        """Print available Phase 0 capabilities"""
        print("\n" + "="*80)
        print("PHASE 0 CAPABILITIES")
        print("="*80)

        capabilities = {
            "📚 Reference Management": [
                "✓ Dynamic reference database loading",
                "✓ Multi-sheet reference support",
                "✓ Item search and lookup",
                "✓ Automatic version tracking",
                "✓ Backup and rollback capability",
                "✓ Reference update without code changes"
            ],
            "🚀 BOM Intake System": [
                "✓ Automated file monitoring",
                "✓ File validation and duplicate detection",
                "✓ Processing queue management",
                "✓ Concurrent file processing",
                "✓ Detailed logging and tracking",
                "✓ File status management (pending/processing/completed/failed)"
            ],
            "🔧 Configuration-Driven": [
                "✓ JSON-based configuration",
                "✓ Dynamic directory structure",
                "✓ Flexible monitoring parameters",
                "✓ Customizable validation rules",
                "✓ Easy to extend and modify"
            ]
        }

        for category, items in capabilities.items():
            print(f"\n{category}")
            for item in items:
                print(f"  {item}")

        print("\n" + "="*80 + "\n")

    def get_next_phases_preview(self):
        """Preview of upcoming phases"""
        phases = {
            "Phase 1": {
                "name": "Configuration System",
                "description": "Flexible BOM format definitions and component mappings",
                "status": "Planned"
            },
            "Phase 2": {
                "name": "Dynamic Data Extraction",
                "description": "Intelligent format detection and flexible data extraction",
                "status": "Planned"
            },
            "Phase 3": {
                "name": "Update Detection & Delta Analysis",
                "description": "Track changes between versions and generate delta reports",
                "status": "Planned"
            },
            "Phase 4": {
                "name": "Version Control & History",
                "description": "Complete version tracking and historical comparison",
                "status": "Planned"
            }
        }

        print("\n" + "="*80)
        print("UPCOMING PHASES PREVIEW")
        print("="*80)

        for phase, info in phases.items():
            print(f"\n{phase}: {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  Status: {info['status']}")

        print("\n" + "="*80 + "\n")


# DEMONSTRATION & TESTING
def demo_phase0():
    """Demonstrate Phase 0 capabilities"""
    print("\n\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  PHASE 0 DEMONSTRATION".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)

    # Initialize
    system = Phase0System()

    # Show capabilities
    system.print_capabilities()

    # Show system status
    system.print_system_overview()

    # Preview next phases
    system.get_next_phases_preview()

    print("\n" + "="*80)
    print("QUICK START EXAMPLES")
    print("="*80)

    print("""
1. SEARCH FOR AN ITEM:
   >>> system.find_item("920-9N62F-00LI-GC0")

2. ADD A REFERENCE DATABASE:
   >>> system.add_reference(
   ...     "new_vendor",
   ...     "NewVendor.xlsx",
   ...     [{"name": "Catalog", "columns": {"model": "A", "pn": "B"}}]
   ... )

3. ADD A BOM FILE FOR PROCESSING:
   >>> system.add_bom_file(
   ...     "new_bom.xlsx",
   ...     metadata={"customer": "NewCustomer", "location": "Boston"}
   ... )

4. START AUTOMATIC MONITORING:
   >>> system.start_monitoring()
   >>> # System will automatically process new files in BOM_INBOX/pending/

5. CHECK QUEUE STATUS:
   >>> status = system.get_queue_status()
   >>> print(status)
    """)

    print("="*80)
    print("\n✅ Phase 0 Setup Complete - Ready for Phase 1 implementation!\n")

    return system


if __name__ == "__main__":
    # Run demonstration
    system = demo_phase0()

    # Keep system accessible for interactive testing
    print("System instance available as: 'system'")
    print("Try: system.find_item('920-9N62F-00LI-GC0')")
