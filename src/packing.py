import math
from typing import Any
from rectpack import newPacker
from utils import scaler

def recursive_packer(algorithm_cls: Any, labels_scaled: dict[tuple[int, int], int], bin_w: int, bin_h: int, rotation: bool, max_bins: int = 256):
    """
    Tenta alocar todos os retângulos recursivamente
    Retorna:
      - placements: lista [(bin_id, x, y, w, h, rid)]
      - used_bins: int (nº de bins adicionados na solução)
      - total_rects: int
    """
    total_rects = sum(labels_scaled.values())
    if total_rects == 0:
        raise ValueError("Nenhum retângulo para alocar.")

    rects_area = scaler(labels_scaled)
    bin_area = bin_w * bin_h
    lower_bound = max(1, math.ceil(rects_area / bin_area))

    count = lower_bound
    while count <= max_bins:
        packer = newPacker(pack_algo=algorithm_cls, rotation=rotation)

        for (w, h), q in labels_scaled.items():
            for _ in range(q):
                packer.add_rect(w, h)

        for _ in range(count):
            packer.add_bin(bin_w, bin_h)

        packer.pack() #type: ignore

        placements = packer.rect_list()  # [(bin_id, x, y, w, h, rid)]
        placed = len(placements)

        if placed >= total_rects:
            return placements, count, total_rects

        count = min(max_bins, count * 2)

    raise RuntimeError(
        f"Não foi possível alocar todos os {total_rects} retângulos até o limite de {max_bins} folhas. "
        "Aumente a folha, reduza espaçamentos, permita rotação, ou suba o limite."
    )

def placements_grouped_mm(placements: list, scale:float, margin_mm: float, spacing_mm: float) -> dict[int, list[tuple[float, float, float, float]]]:
    """Retorno: [(bin_id, x, y, w, h, rid)]"""
    grouped: dict[int, list[tuple[float, float, float, float]]] = {}
    for (b, x, y, w, h, _rid) in placements:
        x_mm = x / scale + margin_mm
        y_mm = y / scale + margin_mm
        w_mm = w / scale - spacing_mm
        h_mm = h / scale - spacing_mm
        grouped.setdefault(b, []).append((x_mm, y_mm, w_mm, h_mm))
    return grouped


def benchmark(placements_mm: list[tuple[float, float, float, float]], page_w_mm: float, page_h_mm: float, margin_mm: float) -> dict[str, float]:
    """Métricas para se determinar o quão efetivo"""
    usable_w = page_w_mm - 2 * margin_mm
    usable_h = page_h_mm - 2 * margin_mm
    usable_area = max(usable_w, 0) * max(usable_h, 0)
    placed_area = sum(max(w, 0) * max(h, 0) for (_x, _y, w, h) in placements_mm)
    util = (placed_area / usable_area * 100) if usable_area > 0 else 0.0
    desperdício = (1 - (placed_area / usable_area)) * 100 if usable_area > 0 else 100.0

    return {
        "area_util_mm2": usable_area,
        "area_colocada_mm2": placed_area,
        "utilizacao_percent": util,
        "desperdicio_mm2": desperdício
    }
