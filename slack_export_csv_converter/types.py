# -*- coding: utf-8 -*-
"""
Defining rather complex types here to improve readability
"""
from typing import Dict, List, Any

# type aliases
ExportFileElement = Dict[str, Any]
ExportFileContent = List[ExportFileElement]
CSVFields = List[str]
CSVData = List[Dict[str, str]]
