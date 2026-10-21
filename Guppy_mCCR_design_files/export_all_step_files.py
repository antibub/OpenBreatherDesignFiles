# Vibe coded by Joseph Hoskinson using Google Gemini

import os
import sys
from pathlib import Path

print("DEBUG: Script started successfully.", flush=True)

# Ensure FreeCAD modules can be imported
try:
    import FreeCAD
    import Part
    print("DEBUG: FreeCAD and Part modules imported successfully.", flush=True)
except ImportError as e:
    print(f"Error importing FreeCAD modules: {e}", flush=True)
    sys.exit(1)

def get_user_inputs():
    """Prompt the user for inputs interactively at runtime."""
    print("\n--- FreeCAD STEP Batch Exporter ---", flush=True)
    
    # Prompt for project root directory
    while True:
        user_root = input("Enter project root directory path: ").strip().strip('"').strip("'")
        root_path = Path(user_root).resolve()
        if root_path.exists() and root_path.is_dir():
            break
        print(f"Error: Directory '{user_root}' does not exist. Please try again.\n")

    # Prompt for file search pattern
    user_pattern = input("Enter file search pattern [default: *.FCStd]: ").strip()
    if not user_pattern:
        user_pattern = "*.FCStd"
        
    return str(root_path), user_pattern

def batch_export_steps(root_dir, file_pattern):
    root_path = Path(root_dir).resolve()
    print(f"\nDEBUG: Looking for CAD folders in root: {root_path}", flush=True)
    print(f"DEBUG: Using file filter pattern: {file_pattern}", flush=True)

    # Find all folders named 'CAD' anywhere within the project structure
    cad_folders = [p for p in root_path.rglob("CAD") if p.is_dir()]
    print(f"DEBUG: Found {len(cad_folders)} 'CAD' folder(s).", flush=True)
    
    if not cad_folders:
        print(f"No 'CAD' folders found within {root_path}", flush=True)
        return

    total_exported = 0

    for cad_dir in cad_folders:
        component_dir = cad_dir.parent
        # Create a 'step_files' folder directly beside the CAD folder
        step_output_dir = component_dir / "step_files"
        
        print(f"\nScanning: {cad_dir.relative_to(root_path)}", flush=True)
        
        fcstd_files = list(cad_dir.rglob(file_pattern))
        print(f"  -> Files matching pattern '{file_pattern}': {[f.name for f in fcstd_files]}", flush=True)
        
        if not fcstd_files:
            print(f"  -> No files matched the pattern '{file_pattern}' in this folder.\n", flush=True)
            continue

        for fcstd_file in fcstd_files:
            # Replicate any subfolder structure (e.g. top_assembly) inside the step_files directory
            rel_path = fcstd_file.relative_to(cad_dir)
            out_file = step_output_dir / rel_path.with_suffix(".step")
            
            # Ensure output subdirectories exist
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"  Processing: {fcstd_file.name}", flush=True)
            
            try:
                doc = FreeCAD.openDocument(str(fcstd_file))
                
                objects_to_export = doc.RootObjects
                if not objects_to_export:
                    objects_to_export = doc.Objects
                    
                if objects_to_export:
                    Part.export(objects_to_export, str(out_file))
                    print(f"    -> Exported to: {out_file.relative_to(root_path)}", flush=True)
                    total_exported += 1
                else:
                    print(f"    -> Warning: No exportable objects found in {fcstd_file.name}", flush=True)
                    
                FreeCAD.closeDocument(doc.Name)
                
            except Exception as e:
                print(f"    -> Error processing {fcstd_file.name}: {e}", flush=True)
        print()

    print(f"Batch export complete! Total files exported: {total_exported}", flush=True)

# Interactive Execution
ROOT_DIR, FILE_PATTERN = get_user_inputs()
batch_export_steps(ROOT_DIR, FILE_PATTERN)








