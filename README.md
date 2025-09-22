# Calculadora de Resistência do Casco v2.1

Ferramenta desenvolvida para cálculo de resistência ao avanço de cascos navais utilizando métodos consagrados da engenharia naval.

## 🚢 Sobre o Projeto

Esta calculadora foi desenvolvida de forma independente, implementando métodos empíricos para estimativa de resistência de cascos de embarcações. A ferramenta é especialmente útil para projetos preliminares e análises comparativas.

## 📋 Funcionalidades Principais

- **Cálculo pelo Método Holtrop & Mennen (1984)**
- **Método simplificado para estimativas rápidas**
- **Interface interativa em português e inglês**
- **Cálculo automático de parâmetros secundários**
- **Geração de gráficos profissionais**
- **Exportação de resultados em CSV**
- **Validação de dados de entrada**

## 🛠️ Instalação

### Pré-requisitos
- Python 3.6 ou superior
- pip (gerenciador de pacotes Python)

### Instalação das Dependências
```bash
# Clone o repositório
git clone https://github.com/italoherodoto/hull-resistance-calculator.git

# Acesse o diretório
cd hull-resistance-calculator

# Instale as dependências
pip install -r requirements.txt
```

## 🎯 Como Usar

### Execução Básica
```bash
python resistance_calculator.py
```

### Fluxo do Programa
1. Selecione o idioma (português/inglês)
2. Informe os parâmetros principais do casco:
   - Comprimento na linha d'água (LWL)
   - Boca (B)
   - Calado (T)
   - Coeficiente de bloco (CB)
3. Defina a faixa de velocidades para análise
4. Escolha o método de cálculo
5. Visualize os resultados
6. Exporte os dados se desejar

### Exemplo de Entrada
```
Comprimento LWL (m) [150.0]: 120
Boca (m) [20.0]: 18
Calado (m) [8.0]: 7.5
Coeficiente de bloco CB [0.70]: 0.72
```

## 📊 Parâmetros Calculados

A ferramenta calcula automaticamente:
- Volume de deslocamento (∇)
- Área molhada (S)
- Coeficiente de seção mestra (CM)
- Centro de carena longitudinal (LCB)
- Área do hélice (APP)

## 📈 Saída dos Resultados

### Dados Numéricos
- Resistência total (kN)
- Resistência de atrito (kN)
- Resistência residual (kN)
- Número de Froude (Fn)
- Número de Reynolds (Re)
- Potência efetiva (kW)

### Gráficos Gerados
1. Resistência vs Velocidade
2. Resistência vs Número de Froude
3. Potência efetiva vs Velocidade

## 🎓 Aplicações Práticas

- Projeto preliminar de embarcações
- Análise de desempenho de cascos
- Estudos comparativos de formas de casco
- Cálculo de requisitos de potência
- Análise de consumo de combustível

## ⚠️ Limitações e Considerações

### Método Holtrop & Mennen
- Desenvolvido para navios mercantes
- Faixa de aplicação: 0.15 < Fn < 0.45
- CB entre 0.55 e 0.85
- L/B entre 3.9 e 14.0

### Método Simplificado
- Aproximação para estudos preliminares
- Menor precisão que métodos completos
- Não considera efeitos de onda

## 📚 Referências Técnicas

- Holtrop, J. & Mennen, G.G.J. (1984). "An approximate power prediction method"
- ITTC (1957). "Recommended Procedures and Guidelines"
- Principles of Naval Architecture (SNAME)

## 🤝 Como Contribuir

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍🎓 Autor

**Italo Herodoto**  
Estudante de Engenharia Naval  
📧 italo.herodoto@ufpe.br  
📧 herodotoitalo2@gmail.com

---

**💡 Dica:** Para melhores resultados, consulte manuais de arquitetura naval para valores típicos de coeficientes para seu tipo de embarcação.

---
# Hull Resistance Calculator v2.1

Tool developed for calculating ship hull resistance using established naval engineering methods.

## 🚢 About the Project

This calculator was independently developed, implementing empirical methods for estimating ship hull resistance. The tool is particularly useful for preliminary designs and comparative analyses.

## 📋 Key Features

- **Calculation using Holtrop & Mennen (1984) Method**
- **Simplified method for quick estimates**
- **Interactive interface in English and Portuguese**
- **Automatic calculation of secondary parameters**
- **Professional graph generation**
- **CSV results export**
- **Input data validation**

## 🛠️ Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Installing Dependencies
```bash
# Clone the repository
git clone https://github.com/italoherodoto/hull-resistance-calculator.git

# Access the directory
cd hull-resistance-calculator

# Install dependencies
pip install -r requirements.txt
```

## 🎯 How to Use

### Basic Execution
```bash
python resistance_calculator.py
```

### Program Flow
1. Select language (English/Portuguese)
2. Enter main hull parameters:
   - Length at Waterline (LWL)
   - Beam (B)
   - Draft (T)
   - Block Coefficient (CB)
3. Set speed range for analysis
4. Choose calculation method
5. View results
6. Export data if desired

### Input Example
```
Length LWL (m) [150.0]: 120
Beam (m) [20.0]: 18
Draft (m) [8.0]: 7.5
Block coefficient CB [0.70]: 0.72
```

## 📊 Calculated Parameters

The tool automatically calculates:
- Displacement volume (∇)
- Wetted surface area (S)
- Midship coefficient (CM)
- Longitudinal center of buoyancy (LCB)
- Propeller area (APP)

## 📈 Results Output

### Numerical Data
- Total resistance (kN)
- Frictional resistance (kN)
- Residual resistance (kN)
- Froude number (Fn)
- Reynolds number (Re)
- Effective power (kW)

### Generated Graphs
1. Resistance vs Speed
2. Resistance vs Froude Number
3. Effective Power vs Speed

## 🎓 Practical Applications

- Preliminary vessel design
- Hull performance analysis
- Comparative hull form studies
- Power requirement calculations
- Fuel consumption analysis

## ⚠️ Limitations and Considerations

### Holtrop & Mennen Method
- Developed for merchant ships
- Application range: 0.15 < Fn < 0.45
- CB between 0.55 and 0.85
- L/B between 3.9 and 14.0

### Simplified Method
- Approximation for preliminary studies
- Lower accuracy than complete methods
- Does not consider wave effects

## 📚 Technical References

- Holtrop, J. & Mennen, G.G.J. (1984). "An approximate power prediction method"
- ITTC (1957). "Recommended Procedures and Guidelines"
- Principles of Naval Architecture (SNAME)

## 🤝 How to Contribute

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📝 License

This project is under MIT License. See the `LICENSE` file for details.

## 👨‍🎓 Author

**Italo Herodoto**  
Naval Engineering Student  
📧 italo.herodoto@ufpe.br  
📧 herodotoitalo2@gmail.com

---

**💡 Tip:** For best results, consult naval architecture manuals for typical coefficient values for your vessel type.
