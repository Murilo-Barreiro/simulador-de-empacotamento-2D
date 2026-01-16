
def scale_bin_dims(width_mm: float, height_mm: float, margin_mm: float, scale: float) -> tuple[int, int]:
    """O pacote rectpack não aceita valores float, sendo necessário uma scala para adequar valores de bins quebrados"""
    bw = int((width_mm - 2 * margin_mm) * scale)
    bh = int((height_mm - 2 * margin_mm) * scale)
    if bw <= 0 or bh <= 0:
        raise ValueError("Dimensões úteis do bin são não positivas. Verifique largura/altura e margens.")
    return bw, bh


def scale_labels(labels_mm: list[tuple[float, float, int]], spacing_mm: float, scale: float) -> dict[tuple[int, int], int]:
    """O pacote rectpack não aceita valores float, sendo necessário uma scala para adequar valores dos rótulos quebrados"""
    out: dict[tuple[int, int], int] = {}
    for altura, largura, qtd in labels_mm:
        if qtd <= 0:
            continue
        w_scaled = int((largura + spacing_mm) * scale)
        h_scaled = int((altura + spacing_mm) * scale)
        if w_scaled <= 0 or h_scaled <= 0:
            raise ValueError("Algum rótulo virou não positivo após a escala. Revise medidas/escala/espaçamento.")
        out[(w_scaled, h_scaled)] = out.get((w_scaled, h_scaled), 0) + int(qtd)
    if not out:
        raise ValueError("Nenhum rótulo válido informado.")
    return out


def scaler(labels_scaled: dict[tuple[int, int], int]) -> int:
    return sum(w * h * q for (w, h), q in labels_scaled.items())
