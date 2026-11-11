import os
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Paths
OUTPUT_DIR = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat"
HTML_PATH = os.path.join(OUTPUT_DIR, "Nexus_Project_Report_Shaikh_Abdul_Zubair.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Nexus_Project_Report_Shaikh_Abdul_Zubair.pdf")
DOCX_PATH = os.path.join(OUTPUT_DIR, "Nexus_Project_Report_Shaikh_Abdul_Zubair.docx")

print("Generating comprehensive academic HTML and DOCX report...")
