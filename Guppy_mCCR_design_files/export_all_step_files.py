import os
import sys
from pathlib import Path

# Ensure FreeCAD modules can be imported if running via FreeCAD's internal python interpreter
try:
    import FreeCAD
    import Part
except ImportError:
    print("Error: This script must be executed using FreeCAD's Python environment or 'freecadcmd'.")
    sys.exit(1)

def batch_export_steps(root_dir, file_pattern="*.FCStd"):
    root_path = Path(root_dir).resolve()
    
    if not root_path.exists():
        print(f"Root directory does not exist: {root_path}")
        return

    # Find all folders named 'CAD' anywhere within the project structure
    cad_folders = [p for p in root_path.rglob("CAD") if p.is_dir()]
    
    if not cad_folders:
        print(f"No 'CAD' folders found within {root_path}")
        return

    print(f"Found {len(cad_folders)} 'CAD' folder(s) to process.\n")
    total_exported = 0

    for cad_dir in cad_folders:
        # The component folder is the parent directory beside the 'CAD' folder
        component_dir = cad_dir.parent
        print(f"Scanning: {cad_dir.relative_to(root_path)}")
        
        # Find matching FreeCAD files inside this specific CAD folder
        fcstd_files = list(cad_dir.rglob(file_pattern))
        
        if not fcstd_files:
            print(f"  -> No files matching pattern '{file_pattern}' found here.\n")
            continue

        for fcstd_file in fcstd_files:
            # Preserve relative subdirectories (e.g., bottom_assembly/top_assembly) inside the component folder
            rel_path = fcstd_file.relative_to(cad_dir)
            out_file = component_dir / rel_path.with_suffix(".step")
            
            # Ensure destination subdirectory exists beside the CAD folder
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"  Processing: {fcstd_file.name}")
            
            try:
                # Open the document in hidden/headless mode
                doc = FreeCAD.openDocument(str(fcstd_file))
                
                # Retrieve root objects (fallback to all objects if root is empty)
                objects_to_export = doc.RootObjects
                if not objects_to_export:
                    objects_to_export = doc.Objects
                    
                if objects_to_export:
                    Part.export(objects_to_export, str(out_file))
                    print(f"    -> Exported to: {out_file.relative_to(root_path)}")
                    total_exported += 1
                else:
                    print(f"    -> Warning: No exportable objects found in {fcstd_file.name}")
                    
                # Close document to free up system memory
                FreeCAD.closeDocument(doc.Name)
                
            except Exception as e:
                print(f"    -> Error processing {fcstd_file.name}: {e}")
        print()

    print(f"Batch export complete! Total files exported: {total_exported}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: freecadcmd /path/to/batch_step_export.py <project_root_path> [file_pattern]")
        print("Example: freecadcmd /path/to/batch_step_export.py /path/to/my_projects \"*assembly*.FCStd\"")
        sys.exit(1)
        
    project_root = sys.argv[1]
    pattern = sys.argv[2] if len(sys.argv) > 2 else "*.FCStd"
    
    batch_export_steps(project_root, pattern)