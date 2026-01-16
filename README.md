
# Simulador de Empacotamento 2D (RectPack Playground)

Este projeto é um **simulador de otimização de corte e empacotamento 2D** (2D Bin Packing), desenvolvido em Python com **Streamlit**. Ele foi criado para auxiliar gráficas e indústrias na redução de desperdício de matéria-prima (folhas adesivas, papel, chapas), utilizando heurísticas clássicas de empacotamento.

## Funcionalidades

- **Múltiplos Algoritmos**: Suporte a heurísticas como *MaxRects*, *Guillotine* e *Skyline* (via biblioteca `rectpack`).
- **Visualização Interativa**: Geração automática de layouts de corte com plotagem visual.
- **Relatórios**: Cálculo de área útil, área ocupada e percentual de desperdício.
- **Modos de Operação**:
  - *Agrupado*: Otimiza o uso das folhas misturando todos os rótulos.
  - *Único*: Gera layouts separados para cada tipo de rótulo.
- **Exportação**: Download dos layouts em **PNG** e **CSV**.

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)**: Interface web interativa.
- **[Rectpack](https://github.com/secnot/rectpack)**: Motor de algoritmos de bin packing.
- **[Matplotlib](https://matplotlib.org/)**: Visualização gráfica dos layouts.
- **[Pandas](https://pandas.pydata.org/)**: Manipulação de dados e exportação CSV.

## Estrutura do Projeto

```
project_root/
├── .streamlit/          # Configurações de tema do Streamlit
├── assets/              # Imagens e logos estáticos
├── src/                 # Código fonte da aplicação
│   ├── app.py           # Ponto de entrada (Main)
│   ├── pacing_logic.py  # Lógica de empacotamento
│   ├── plotting.py      # Funções de plotagem
│   └── utils.py         # Funções auxiliares
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação
```

## Execução

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado)**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**:
   ```bash
   streamlit run src/app.py
   ```

Acesse o navegador no endereço indicado (geralmente `http://localhost:8501`).
