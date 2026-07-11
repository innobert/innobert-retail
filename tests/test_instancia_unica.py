def test_adquirir_instancia_unica_preven_segunda():
    from inicio import adquirir_instancia_unica

    sock1 = adquirir_instancia_unica()
    assert sock1 is not None

    # Segunda adquisición debe fallar (devuelve None)
    sock2 = adquirir_instancia_unica()
    assert sock2 is None

    # Liberar para no interferir con otras pruebas
    try:
        sock1.close()
    except Exception:
        pass
