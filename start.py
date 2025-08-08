#!/usr/bin/env python3
import sys
from pathlib import Path

# Ajouter le dossier src au path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from verbiage import main

if __name__ == "__main__":
    main()
