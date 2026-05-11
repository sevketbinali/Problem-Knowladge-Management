from src.domain.models import IshikawaData

def test_ishikawa_circularity_detection():
    # Case 1: No circularity
    data = IshikawaData(
        man=["Operator error"],
        machine=["Broken tool"],
        method=[],
        material=[],
        measurement=[],
        environment=[]
    )
    assert data.check_circularity() == []

    # Case 2: Direct circularity (Human -> Machine -> Human)
    data = IshikawaData(
        man=["Operator error due to Machine malfunction"],
        machine=["Machine failure caused by Human error"],
        method=[],
        material=[],
        measurement=[],
        environment=[]
    )
    warnings = data.check_circularity()
    assert len(warnings) > 0
    assert any("man -> machine -> man" in w or "machine -> man -> machine" in w for w in warnings)

    # Case 3: Complex circularity (Human -> Machine -> Method -> Human)
    data = IshikawaData(
        man=["Human error in Machine operation"],
        machine=["Machine failure due to bad Process"],
        method=["Process issue caused by Human"],
        material=[],
        measurement=[],
        environment=[]
    )
    warnings = data.check_circularity()
    assert len(warnings) > 0
    assert any("man -> machine -> method -> man" in w for w in warnings)

def test_ishikawa_no_false_positive():
    # Mentions same category keyword
    data = IshikawaData(
        man=["Human error by person"],
        machine=[],
        method=[],
        material=[],
        measurement=[],
        environment=[]
    )
    assert data.check_circularity() == []
