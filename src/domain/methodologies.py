"""Methodology engine for managing different problem-solving frameworks (Ishikawa, 8D, etc.)."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.domain.models import MethodologyType


class MethodologyTemplate(ABC):
    @property
    @abstractmethod
    def name(self) -> MethodologyType:
        pass

    @property
    @abstractmethod
    def steps(self) -> List[str]:
        pass

    @abstractmethod
    def get_step_prompt(self, step_index: int) -> str:
        pass


class IshikawaTemplate(MethodologyTemplate):
    name = MethodologyType.ISHIKAWA
    steps = [
        "Man (Human)",
        "Machine",
        "Method",
        "Material",
        "Measurement",
        "Environment"
    ]

    def get_step_prompt(self, step_index: int) -> str:
        kategori = self.steps[step_index]
        return f"Lütfen '{kategori}' kategorisi altındaki olası kök nedenleri belirtiniz."


class FiveWhyTemplate(MethodologyTemplate):
    name = MethodologyType.FIVE_WHY
    # 5 Why adımları dinamiktir, ancak temel bir yapı sunulabilir.
    steps = ["Why 1", "Why 2", "Why 3", "Why 4", "Why 5"]

    def get_step_prompt(self, step_index: int) -> str:
        if step_index == 0:
            return "Bu problem neden oluşuyor? (İlk 'Neden')"
        return f"{step_index + 1}. Neden nedir?"


class EightDTemplate(MethodologyTemplate):
    name = MethodologyType.EIGHT_D
    steps = [
        "D1: Team",
        "D2: Problem Description",
        "D3: Containment Plan",
        "D4: Root Cause Analysis",
        "D5: Corrective Actions",
        "D6: Validation",
        "D7: Preventive Actions",
        "D8: Team Recognition"
    ]

    def get_step_prompt(self, step_index: int) -> str:
        disiplin = self.steps[step_index]
        return f"Lütfen {disiplin} adımını tamamlayınız."


class PDCATemplate(MethodologyTemplate):
    name = MethodologyType.PDCA
    steps = ["Plan", "Do", "Check", "Act"]

    def get_step_prompt(self, step_index: int) -> str:
        adim = self.steps[step_index]
        return f"Lütfen '{adim}' adımına dair bilgileri giriniz."


class MethodologyEngine:
    def __init__(self):
        self._templates: Dict[MethodologyType, MethodologyTemplate] = {
            MethodologyType.ISHIKAWA: IshikawaTemplate(),
            MethodologyType.FIVE_WHY: FiveWhyTemplate(),
            MethodologyType.EIGHT_D: EightDTemplate(),
            MethodologyType.PDCA: PDCATemplate()
        }

    def get_template(self, methodology: MethodologyType) -> MethodologyTemplate:
        if methodology not in self._templates:
            raise ValueError(f"Unsupported methodology: {methodology}")
        return self._templates[methodology]

    def get_step_count(self, methodology: MethodologyType) -> int:
        return len(self.get_template(methodology).steps)

    def is_complete(self, methodology: MethodologyType, responses: Dict[str, Any]) -> bool:
        """Check if all required steps for a methodology are completed."""
        template = self.get_template(methodology)
        # Check if we have responses for all steps
        # This is a basic check; specific methodologies might have more complex logic.
        return len(responses) >= len(template.steps)
