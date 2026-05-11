from typing import Dict, List, Optional, Any
from src.domain.models import MethodologyType

class MethodologyStep:
    def __init__(self, name: str, question: str, description: Optional[str] = None):
        self.name = name
        self.question = question
        self.description = description

class MethodologyTemplate:
    def __init__(self, methodology_type: MethodologyType, steps: List[MethodologyStep]):
        self.methodology_type = methodology_type
        self.steps = steps

class MethodologyEngine:
    """Engine to manage different problem solving methodologies and their steps."""
    
    TEMPLATES: Dict[MethodologyType, MethodologyTemplate] = {
        MethodologyType.ISHIKAWA: MethodologyTemplate(
            MethodologyType.ISHIKAWA,
            [
                MethodologyStep("Human", "İnsan (Man) faktörü ile ilgili olası nedenler nelerdir?"),
                MethodologyStep("Machine", "Makine (Machine) faktörü ile ilgili olası nedenler nelerdir?"),
                MethodologyStep("Method", "Yöntem (Method) faktörü ile ilgili olası nedenler nelerdir?"),
                MethodologyStep("Material", "Malzeme (Material) faktörü ile ilgili olası nedenler nelerdir?"),
                MethodologyStep("Measurement", "Ölçüm (Measurement) faktörü ile ilgili olası nedenler nelerdir?"),
                MethodologyStep("Environment", "Çevre (Environment) faktörü ile ilgili olası nedenler nelerdir?"),
            ]
        ),
        MethodologyType.FIVE_WHY: MethodologyTemplate(
            MethodologyType.FIVE_WHY,
            [
                MethodologyStep("Why 1", "Bu problem neden oluşuyor?"),
                MethodologyStep("Why 2", "Peki, bu durum neden kaynaklanıyor?"),
                MethodologyStep("Why 3", "Bunun arkasındaki temel sebep nedir?"),
                MethodologyStep("Why 4", "Bu neden meydana geliyor?"),
                MethodologyStep("Why 5", "Kök neden olarak neyi tanımlarsınız?"),
                # Note: 5 Why can have 3-7 steps. We define 5 as default, 
                # but the session logic will handle the dynamic flow (3-7 range).
            ]
        ),
        MethodologyType.EIGHT_D: MethodologyTemplate(
            MethodologyType.EIGHT_D,
            [
                MethodologyStep("D1", "Ekip Oluşturma (Team): Problemi çözecek ekibi tanımlayın.", "Kimler dahil? Rolleri neler?"),
                MethodologyStep("D2", "Problem Tanımı (Problem Description): Problemi detaylandırın.", "Ne oldu? Nerede? Ne zaman?"),
                MethodologyStep("D3", "Geçici Önlemler (Containment): Acil müdahale olarak ne yapıldı?", "Müşteriyi/üretimi korumak için ne yapıldı?"),
                MethodologyStep("D4", "Kök Neden Analizi (Root Cause): Temel sebep nedir?", "Neden kaçtı? Neden oluştu?"),
                MethodologyStep("D5", "Düzeltici Eylemler (Corrective Actions): Kalıcı çözüm planınız nedir?", "Nasıl düzeltilecek?"),
                MethodologyStep("D6", "Uygulama (Validation): Çözümün işe yaradığını nasıl doğruladınız?", "Sonuçlar nedir?"),
                MethodologyStep("D7", "Önleme (Prevention): Benzer sorunların tekrarını nasıl engelleyeceksiniz?", "Sistemde ne değişti?"),
                MethodologyStep("D8", "Kapanış (Closure): Ekip başarısını kutlayın ve kaydı kapatın.", "Dersler paylaşıldı mı?"),
            ]
        ),
        MethodologyType.PDCA: MethodologyTemplate(
            MethodologyType.PDCA,
            [
                MethodologyStep("Plan", "Plan: Hedefi ve süreci planlayın."),
                MethodologyStep("Do", "Do: Planı uygulayın."),
                MethodologyStep("Check", "Check: Sonuçları kontrol edin."),
                MethodologyStep("Act", "Act: Önlem alın veya süreci standartlaştırın."),
            ]
        )
    }

    @classmethod
    def get_template(cls, methodology_type: MethodologyType) -> MethodologyTemplate:
        """Returns the template for a given methodology."""
        if methodology_type not in cls.TEMPLATES:
            raise ValueError(f"Unsupported methodology: {methodology_type}")
        return cls.TEMPLATES[methodology_type]

    @classmethod
    def get_step(cls, methodology_type: MethodologyType, step_index: int) -> Optional[MethodologyStep]:
        """Returns a specific step by index for a methodology."""
        template = cls.get_template(methodology_type)
        if 0 <= step_index < len(template.steps):
            return template.steps[step_index]
        return None

    @classmethod
    def is_complete(cls, methodology_type: MethodologyType, step_index: int) -> bool:
        """Checks if all steps in a methodology are completed based on current index."""
        template = cls.get_template(methodology_type)
        return step_index >= len(template.steps)
