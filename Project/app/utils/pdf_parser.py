import PyPDF2
import re
from typing import Dict, Any

class DegreeAuditParser:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.text = self._extract_text()
        self.requirements = {}
    
    def _extract_text(self) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(self.pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def parse_requirements(self) -> Dict[str, Any]:
        """Parse all requirements from the degree audit text"""
        self._parse_composition()
        self._parse_quantitative_reasoning()
        self._parse_cultural_studies()
        self._parse_language_requirement()
        self._parse_general_education()
        return self.requirements
    
    def _parse_composition(self):
        """Parse composition requirements"""
        # UNIVERSITY COMPOSITION I REQUIREMENT
        comp1_pattern = r'UNIVERSITY COMPOSITION I REQUIREMENT.*?(OK|COMPLETE|NEEDS|NO)'
        comp1_match = re.search(comp1_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['composition1'] = comp1_match.group(1) in ['OK', 'COMPLETE'] if comp1_match else False
        
        # ADVANCED COMPOSITION
        adv_comp_pattern = r'ADVANCED COMPOSITION.*?(OK|COMPLETE|NEEDS|NO)'
        adv_comp_match = re.search(adv_comp_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['advanced_composition'] = adv_comp_match.group(1) in ['OK', 'COMPLETE'] if adv_comp_match else False
    
    def _parse_quantitative_reasoning(self):
        """Parse quantitative reasoning requirements"""
        # QUANTITATIVE REASONING I
        qr1_pattern = r'QUANTITATIVE REASONING I.*?(OK|COMPLETE|IP|NEEDS|NO)'
        qr1_match = re.search(qr1_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['quantitative_reasoning1'] = qr1_match.group(1) in ['OK', 'COMPLETE', 'IP'] if qr1_match else False
        
        # QUANTITATIVE REASONING II
        qr2_pattern = r'QUANTITATIVE REASONING II.*?(OK|COMPLETE|IP|NEEDS|NO)'
        qr2_match = re.search(qr2_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['quantitative_reasoning2'] = qr2_match.group(1) in ['OK', 'COMPLETE', 'IP'] if qr2_match else False
    
    def _parse_cultural_studies(self):
        """Parse cultural studies requirements"""
        # WESTERN/COMPARATIVE CULTURE(S)
        western_pattern = r'WESTERN/COMPARATIVE CULTURE.*?(OK|COMPLETE|NEEDS|NO)'
        western_match = re.search(western_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['western_culture'] = western_match.group(1) in ['OK', 'COMPLETE'] if western_match else False
        
        # NON-WESTERN CULTURE(S)
        non_western_pattern = r'NON-WESTERN CULTURE.*?(OK|COMPLETE|NEEDS|NO)'
        non_western_match = re.search(non_western_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['non_western_culture'] = non_western_match.group(1) in ['OK', 'COMPLETE'] if non_western_match else False
        
        # U.S. MINORITY CULTURE(S)
        us_minority_pattern = r'U\.S\. MINORITY CULTURE.*?(OK|COMPLETE|NEEDS|NO)'
        us_minority_match = re.search(us_minority_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['us_minority_culture'] = us_minority_match.group(1) in ['OK', 'COMPLETE'] if us_minority_match else False
    
    def _parse_language_requirement(self):
        """Parse language requirement"""
        language_pattern = r'LANGUAGE REQUIREMENT.*?(OK|COMPLETE|NEEDS|NO)'
        language_match = re.search(language_pattern, self.text, re.IGNORECASE | re.DOTALL)
        self.requirements['language_requirement'] = language_match.group(1) in ['OK', 'COMPLETE'] if language_match else False
    
    def _parse_general_education(self):
        """Parse general education categories"""
        # For simplicity, we'll set these based on course completion patterns
        # In a real implementation, you'd parse the specific course lists
        self.requirements['humanities_arts'] = 'HUMANITIES AND THE ARTS' in self.text
        self.requirements['social_behavioral'] = 'SOCIAL AND BEHAVIORAL SCIENCE' in self.text
        self.requirements['natural_sciences'] = 'NATURAL SCIENCES AND TECHNOLOGY' in self.text
        
        # Set subcategories to True for now (you can enhance parsing as needed)
        self.requirements['humanities_hp'] = True
        self.requirements['humanities_la'] = True
        self.requirements['social_behavioral_bsc'] = True
        self.requirements['social_behavioral_ss'] = True
        self.requirements['natural_sciences_ls'] = True
        self.requirements['natural_sciences_ps'] = True