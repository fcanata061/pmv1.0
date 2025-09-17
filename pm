#!/usr/bin/env python3
"""
Comando do sistema para PM
Permite usar: pm i gcc-stage1, pm b firefox, pm up all, pm s vim
"""
import sys
from main import main  # main.py precisa ter função main()

if __name__ == "__main__":
    sys.exit(main())
