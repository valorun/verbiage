#!/usr/bin/env python3
import sys
from pathlib import Path

# Ajouter le dossier parent au path pour résoudre les imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.verbiage import main

if __name__ == "__main__":
    main()
