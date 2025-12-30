from rossfilter.units import kev_to_ev, um_to_cm


def test_kev_to_ev():
    assert kev_to_ev(1.0) == 1000.0


def test_um_to_cm():
    assert um_to_cm(100.0) == 0.01
