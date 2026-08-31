import pathlib

def cleanup():
    root = pathlib.Path(__file__).resolve().parents[1]
    raw_dir = root / 'data' / 'corpus' / 'raw_downloads'
    extracted_dir = root / 'data' / 'corpus' / 'extracted'
    
    removed_count = 0
    
    if not raw_dir.exists():
        print("Raw downloads directory not found.")
        return

    for pdf_path in raw_dir.glob('*.pdf'):
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(5)
            
            # A valid PDF must start with %PDF-
            if header != b'%PDF-':
                print(f"Removing fake PDF: {pdf_path.name}")
                pdf_path.unlink()
                removed_count += 1
                
                # Remove corresponding extracted text if it exists
                txt_name = pdf_path.stem + '.txt'
                txt_path = extracted_dir / txt_name
                if txt_path.exists():
                    txt_path.unlink()
                    print(f"  -> Removed corresponding fake extracted text: {txt_name}")
                    
        except Exception as e:
            print(f"Error checking {pdf_path.name}: {e}")

    print(f"\nCleanup complete! Removed {removed_count} fake/empty files.")

if __name__ == "__main__":
    cleanup()
