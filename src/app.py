import io
import pandas as pd
import streamlit as st
from rectpack import MaxRectsBssf, GuillotineBlsfSas, SkylineMwfl

from utils import scale_bin_dims, scale_labels
from packing import recursive_packer, placements_grouped_mm, benchmark
from plotting import fig_from_layout

def main():
    st.set_page_config(page_title="RectPack Playground", layout="wide")
    st.title("Simulador de Empacotamento 2D - Estudo de caso em uma Gráfica de rótulos adesivos")

    with st.sidebar:
        st.header("Folha (mm)")
        page_w = st.number_input("Largura da folha (mm)", value=485.0, min_value=1.0, step=1.0)
        page_h = st.number_input("Altura da folha (mm)", value=500.0, min_value=1.0, step=1.0)

        st.header("Layout")
        margin = st.number_input("Margem (mm)", value=7.5, min_value=0.0, step=0.5)
        spacing = st.number_input("Espaçamento entre rótulos (mm)", value=4.3, min_value=0.0, step=0.1)

        st.header("Escala")
        scale = st.number_input("Fator de escala (px/mm)", value=10.0, min_value=0.1, step=0.1)

        st.header("Heurísticas")
        alg_map = {
            "MaxRectsBssf": MaxRectsBssf,
            "GuillotineBlsfSas": GuillotineBlsfSas,
            "SkylineMwfl": SkylineMwfl,
        }
        alg_choices = st.multiselect("Selecione uma ou mais heurísticas", list(alg_map.keys()),
                                     default=["MaxRectsBssf", "GuillotineBlsfSas", "SkylineMwfl"])
        
        rotation = st.toggle("Permitir rotação", value=True)

        st.header("Limites")
        max_bins = st.number_input("Máximo de folhas (proteção)", value=64, min_value=1, step=1)

        st.header("Modo")
        mode = st.select_slider(
            "Modo de empacotamento",
            options=["Agrupado", "Único"],
            value="Agrupado",
            help='Modo "Agrupado" traz todos os rótulos junto no mesmo grid. Modo "Único" aplica todas as heurísticas escolhidas em cada objeto'
        )

    st.subheader("Rótulos (mm)")
    st.write("Edite a tabela: altura, largura e quantidade.")

    default_rows = [
        {"altura_mm": 29.0,  "largura_mm": 53.4, "qtd": 4},
        {"altura_mm": 142.6, "largura_mm": 75.7, "qtd": 4},
        {"altura_mm": 90.3,  "largura_mm": 24.0, "qtd": 4},
        {"altura_mm": 170.6, "largura_mm": 146.4, "qtd": 4},
    ]
    df = st.data_editor(
        default_rows,
        num_rows="dynamic",
        column_config={
            "altura_mm": st.column_config.NumberColumn("Altura (mm)", step=0.1, min_value=0.0),
            "largura_mm": st.column_config.NumberColumn("Largura (mm)", step=0.1, min_value=0.0),
            "qtd": st.column_config.NumberColumn("Qtd", step=1, min_value=0),
        }
    )

    btn = st.button("Gerar layouts", type="primary")

    if btn:
        try:
            labels_input: list[tuple[float, float, int]] = []
            for row in df:
                try:
                    a = float(row["altura_mm"])
                    l = float(row["largura_mm"])
                    q = int(row["qtd"])
                except Exception:
                    continue
                if a > 0 and l > 0 and q > 0:
                    labels_input.append((a, l, q))
            if not labels_input:
                st.error("Informe ao menos um rótulo válido (altura > 0, largura > 0, qtd > 0).")
                st.stop()

            bin_w, bin_h = scale_bin_dims(page_w, page_h, margin, scale)
            labels_scaled = scale_labels(labels_input, spacing, scale)

            for alg_name in alg_choices:
                algorithm_cls = alg_map[alg_name]
                st.markdown(f"## Heurística: {alg_name}")

                desperdicio_total = []
                if mode == "Agrupado":
                    #MODO AGRUPADO 
                    placements, used_bins, total_rects = recursive_packer(algorithm_cls, labels_scaled, bin_w, bin_h, rotation, max_bins=int(max_bins))

                    grouped_mm = placements_grouped_mm(placements, scale, margin, spacing)
                    bin_ids_sorted = sorted(grouped_mm.keys())

                    rows = []
                    for b in bin_ids_sorted:
                        for (x, y, w, h) in grouped_mm[b]:
                            rows.append({"bin_id": b, "x_mm": x, "y_mm": y, "w_mm": w, "h_mm": h})
                    csv_df = pd.DataFrame(rows, columns=["bin_id", "x_mm", "y_mm", "w_mm", "h_mm"])
                    st.download_button(
                        label=f"Baixar CSV ({alg_name}) — modo agrupado",
                        data=csv_df.to_csv(index=False).encode("utf-8"),
                        file_name=f"grid_{alg_name}_agrupado.csv",
                        mime="text/csv"
                    )

                    tabs = st.tabs([f"Folha {i+1}" for i in range(len(bin_ids_sorted))])
                    for idx, b in enumerate(bin_ids_sorted):
                        with tabs[idx]:
                            placements_mm = grouped_mm[b]
                            fig = fig_from_layout(
                                placements_mm, page_w, page_h, margin,
                                title=f"{alg_name} — Folha {idx+1}/{len(bin_ids_sorted)} (Agrupado)"
                            )
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.pyplot(fig, clear_figure=True)
                            with col2:
                                stats = benchmark(placements_mm, page_w, page_h, margin)
                                st.markdown(f"**Métricas (Folha {idx+1})**")
                                st.write(f"Área útil (mm²): **{stats['area_util_mm2']:.0f}**")
                                st.write(f"Área colocada (mm²): **{stats['area_colocada_mm2']:.0f}**")
                                st.write(f"Desperdício de matéria prima (mm²): **{stats['desperdicio_mm2']:.2f}%**")
                                desperdicio_total.append(stats['desperdicio_mm2'])

                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
                            buf.seek(0)
                            st.download_button(
                                label=f"Baixar PNG (Folha {idx+1})",
                                data=buf,
                                file_name=f"grid_{alg_name}_agrupado_folha_{idx+1}.png",
                                mime="image/png",
                                key=f"png_{alg_name}_agr_{idx}"
                            )
                    if desperdicio_total:
                        avg_desp = sum(desperdicio_total) / len(desperdicio_total)
                        st.markdown(f"**Desperdício médio de matéria prima (todas as folhas): {avg_desp:.2f}%**")

                else:
                    #MODO ÚNICO
                    def type_label_from_scaled(w_int: int, h_int: int) -> str:
                        w_mm_real = w_int / scale - spacing
                        h_mm_real = h_int / scale - spacing
                        return f"{w_mm_real:.1f}x{h_mm_real:.1f} mm"

                    type_keys_sorted = sorted(labels_scaled.keys(), key=lambda wh: (wh[0]*wh[1], wh[0], wh[1]))
                    outer_tabs = st.tabs([f"{type_label_from_scaled(*wh)}" for wh in type_keys_sorted])


                    all_rows = []
                    for idx_type, wh in enumerate(type_keys_sorted):
                        w_int, h_int = wh
                        q = labels_scaled[wh]
                        label_txt = type_label_from_scaled(w_int, h_int)

                        # Single bin packing call per type
                        placements, used_bins, total_rects = recursive_packer(algorithm_cls, {wh: q}, bin_w, bin_h, rotation, max_bins=int(max_bins))

                        grouped_mm = placements_grouped_mm(placements, scale, margin, spacing)
                        bin_ids_sorted = sorted(grouped_mm.keys())

                        with outer_tabs[idx_type]:
                            st.markdown(f"**Tipo:** {label_txt} — **Qtd:** {q} — **Folhas usadas:** {len(bin_ids_sorted)}")

                            inner_tabs = st.tabs([f"Folha {i+1}" for i in range(len(bin_ids_sorted))])
                            for idx_bin, b in enumerate(bin_ids_sorted):
                                with inner_tabs[idx_bin]:
                                    placements_mm = grouped_mm[b]
                                    fig = fig_from_layout(
                                        placements_mm, page_w, page_h, margin,
                                        title=f"{alg_name} — {label_txt} — Folha {idx_bin+1}/{len(bin_ids_sorted)} (Único por tipo)"
                                    )

                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.pyplot(fig, clear_figure=True)
                                    with col2:
                                        stats = benchmark(placements_mm, page_w, page_h, margin)
                                        st.markdown(f"**Métricas (Folha {idx_bin+1})**")
                                        st.write(f"Área útil (mm²): **{stats['area_util_mm2']:.0f}**")
                                        st.write(f"Área colocada (mm²): **{stats['area_colocada_mm2']:.0f}**")
                                        st.write(f"Desperdício de matéria prima (mm²): **{stats['desperdicio_mm2']:.2f}%**")

                                    buf = io.BytesIO()
                                    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
                                    buf.seek(0)
                                    st.download_button(
                                        label=f"Baixar PNG ({label_txt}) — Folha {idx_bin+1}",
                                        data=buf,
                                        file_name=f"grid_{alg_name}_unico_{label_txt.replace('x','x').replace(' ','')}_folha_{idx_bin+1}.png",
                                        mime="image/png",
                                        key=f"png_{alg_name}_unico_{idx_type}_{idx_bin}"
                                    )

                                    for (x, y, w, h) in placements_mm:
                                        all_rows.append({
                                            "tipo_w_mm": float(f"{w_int/scale - spacing:.3f}"),
                                            "tipo_h_mm": float(f"{h_int/scale - spacing:.3f}"),
                                            "bin_id": int(b),
                                            "x_mm": x, "y_mm": y, "w_mm": w, "h_mm": h
                                        })

                    if all_rows:
                        csv_df = pd.DataFrame(all_rows, columns=["tipo_w_mm", "tipo_h_mm", "bin_id", "x_mm", "y_mm", "w_mm", "h_mm"])
                        st.download_button(
                            label=f"Baixar CSV ({alg_name}) — modo único por tipo",
                            data=csv_df.to_csv(index=False).encode("utf-8"),
                            file_name=f"grid_{alg_name}_unico_por_tipo.csv",
                            mime="text/csv"
                        )

        except Exception as e:
            st.error(f"Falha ao gerar layout: {e}")

if __name__ == "__main__":
    main()
