from utils.bills import fix_bill_id


def test_fix_bill_id():
    assert fix_bill_id("HB1") == "HB 1"
    assert fix_bill_id("HB 0001") == "HB 1"
    assert fix_bill_id("SJRA") == "SJR A"
