"""
HULL RESISTANCE CALCULATOR v2.1
Método Holtrop & Mennen (1984)
Autor: Italo Herodoto - Estudante de Engenharia Naval (UFPE)
"""

import sys
import subprocess
import importlib
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Union, List, Optional
import csv
from datetime import datetime
import os

# --- INSTALAÇÃO AUTOMÁTICA DE DEPENDÊNCIAS ---
def install_package(package_name):
    """Instala pacote automaticamente se não estiver disponível"""
    try:
        importlib.import_module(package_name.split('.')[0])
        return True
    except ImportError:
        print(f"Instalando {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return True
        except:
            print(f"Falha ao instalar {package_name}")
            return False

# Lista de dependências necessárias
REQUIRED_PACKAGES = ['numpy', 'pandas', 'matplotlib']

# Instala automaticamente o que faltar
for package in REQUIRED_PACKAGES:
    install_package(package)

import matplotlib.pyplot as plt
plt.style.use('default')

# --- CONFIGURAÇÃO GLOBAL ---
class Config:
    """Configurações globais do programa"""
    WATER_DENSITY = 1025  # kg/m³ (água do mar)
    KINEMATIC_VISCOSITY = 1.1892e-6  # m²/s (15°C)
    GRAVITY = 9.81  # m/s²
    LANGUAGE = 'english'

# --- CLASSES PRINCIPAIS ---
@dataclass
class HullParameters:
    """Parâmetros geométricos do casco com validação"""
    
    L: float  # Comprimento na linha d'água [m]
    B: float  # Boca [m]
    T: float  # Calado [m]
    CB: float  # Coeficiente de bloco
    CM: Optional[float] = None
    LCB: Optional[float] = None
    S: Optional[float] = None
    V: Optional[float] = None
    APP: Optional[float] = None
    
    def __post_init__(self):
        """Valida e completa os parâmetros automaticamente"""
        self._validate_parameters()
        self._calculate_missing_parameters()
    
    def _validate_parameters(self):
        """Valida os parâmetros básicos com mensagens detalhadas"""
        errors = []
        
        if self.L <= 0:
            errors.append("Comprimento deve ser positivo")
        if self.B <= 0:
            errors.append("Boca deve ser positiva") 
        if self.T <= 0:
            errors.append("Calado deve ser positivo")
        if not (0.3 <= self.CB <= 1.0):
            errors.append(f"Coeficiente de bloco (CB={self.CB}) deve estar entre 0.3 e 1.0")
            errors.append("Dica: Para barcos rápidos, use CB entre 0.35-0.45")
        
        if errors:
            error_msg = "Erros de validação:\n- " + "\n- ".join(errors)
            raise ValueError(error_msg)
    
    def _calculate_missing_parameters(self):
        """Calcula parâmetros faltantes usando fórmulas aproximadas"""
        # Volume de deslocamento (Δ = L × B × T × CB)
        if self.V is None:
            self.V = self.L * self.B * self.T * self.CB
        
        # Área molhada (Fórmula de Holtrop para navios mercantes)
        if self.S is None:
            self.S = self.L * (2 * self.T + self.B) * np.sqrt(self.CB) * (
                0.453 + 0.4425 * self.CB - 0.2862 * self.CB**2 - 
                0.003467 * self.B/self.T + 0.3696 * self.CB * self.B/self.T
            ) + 2.38 * self.V / self.CB / self.L
        
        # Coeficiente de seção mestra (valor típico)
        if self.CM is None:
            self.CM = 0.98
        
        # Centro de carena longitudinal (centro do casco)
        if self.LCB is None:
            self.LCB = 0.5
        
        # Área do hélice (estimativa baseada no calado)
        if self.APP is None:
            self.APP = 0.5 * np.pi * (0.7 * self.T)**2

    def summary(self, language: str = None) -> str:
        """Retorna resumo formatado dos parâmetros"""
        lang = language or Config.LANGUAGE
        
        if lang == 'portuguese':
            return f"""
            PARÂMETROS DO CASCO:
            --------------------
            Comprimento (LWL): {self.L:.2f} m
            Boca (B): {self.B:.2f} m
            Calado (T): {self.T:.2f} m
            Coef. Bloco (CB): {self.CB:.3f}
            Coef. Seção Mestra (CM): {self.CM:.3f}
            Centro de Carena (LCB): {self.LCB:.1f}% L
            Volume Deslocamento: {self.V:,.0f} m³
            Área Molhada: {self.S:,.0f} m²
            Área do Hélice: {self.APP:.1f} m²
            """
        else:
            return f"""
            HULL PARAMETERS:
            --------------------
            Length (LWL): {self.L:.2f} m
            Beam (B): {self.B:.2f} m
            Draft (T): {self.T:.2f} m
            Block Coefficient (CB): {self.CB:.3f}
            Midship Coefficient (CM): {self.CM:.3f}
            Longitudinal Center (LCB): {self.LCB:.1f}% L
            Displacement Volume: {self.V:,.0f} m³
            Wetted Surface Area: {self.S:,.0f} m²
            Propeller Area: {self.APP:.1f} m²
            """

class ResistanceCalculator:
    """Calculadora de resistência com múltiplos métodos"""
    
    def __init__(self, hull_params: HullParameters):
        self.hull = hull_params
        self.results = None
    
    def calculate_holtrop(self, speeds: Union[float, List[float], np.ndarray]) -> dict:
        """
        Calcula resistência pelo método Holtrop & Mennen (1984)
        
        Equações base:
        1. Resistência Friccional: RF = 0.5 × ρ × V² × S × CF
        2. Número de Reynolds: Rn = (V × L) / ν
        3. Coeficiente de Fricção: CF = 0.075 / (log10(Rn) - 2)²
        4. Resistência Residual: RR = Δ × ρ × g × fatores_correção
        5. Resistência Total: RT = RF + RR
        """
        speeds = np.asarray(speeds)
        Fn = speeds / np.sqrt(Config.GRAVITY * self.hull.L)  # Número de Froude
        
        # 1. Resistência Friccional (ITTC-1957)
        Rn = speeds * self.hull.L / Config.KINEMATIC_VISCOSITY
        CF = 0.075 / (np.log10(Rn) - 2)**2
        RF = 0.5 * Config.WATER_DENSITY * speeds**2 * self.hull.S * CF
        
        # 2. Resistência Residual (Holtrop & Mennen simplificado)
        c1 = 2223105 * (self.hull.B/self.hull.L)**1.07961 * (90 - 0.3)**(-1.37565)
        c2 = np.exp(-1.89 * np.sqrt(c1))
        c3 = 0.56 * (self.hull.B * self.hull.T)**1.5 / (
            self.hull.V * (0.31 * np.sqrt(self.hull.B * self.hull.T) + self.hull.T))
        
        c12 = self.hull.L**3 / self.hull.V
        c13 = 1 + 0.003 * self.hull.LCB
        
        RR = self.hull.V * Config.WATER_DENSITY * Config.GRAVITY * c2 * c3 * c12**0.004 * np.exp(-0.9/Fn) * c13
        
        # 3. Resistência Total
        RTotal = RF + RR
        
        self.results = {
            'speed_mps': speeds,
            'speed_knots': speeds * 1.944,
            'froude': Fn,
            'reynolds': Rn,
            'resistance_total_N': RTotal,
            'resistance_total_kN': RTotal / 1000,
            'resistance_friction_N': RF,
            'residual_resistance_N': RR,
            'cf_coefficient': CF,
            'effective_power_kW': RTotal * speeds / 1000  # Potência efetiva
        }
        
        return self.results
    
    def calculate_simple(self, speeds: Union[float, List[float], np.ndarray]) -> dict:
        """
        Método simplificado para estimativa rápida
        RT = 0.5 × ρ × V² × S × (C₁ + C₂ × Fn²)
        """
        speeds = np.asarray(speeds)
        Fn = speeds / np.sqrt(Config.GRAVITY * self.hull.L)
        
        RTotal = 0.5 * Config.WATER_DENSITY * speeds**2 * self.hull.S * (
            0.001 + 0.002 * Fn**2
        )
        
        self.results = {
            'speed_mps': speeds,
            'speed_knots': speeds * 1.944,
            'froude': Fn,
            'resistance_total_N': RTotal,
            'resistance_total_kN': RTotal / 1000,
            'effective_power_kW': RTotal * speeds / 1000
        }
        
        return self.results

    def export_results(self, filename: str = None) -> str:
        """Exporta resultados para CSV"""
        if self.results is None:
            raise ValueError("Execute o cálculo primeiro")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resistance_results_{timestamp}.csv"
        
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False, float_format='%.4f')
        return filename
    
    def plot_results(self, save_path: str = None, language: str = None):
        """Gráficos profissionais dos resultados"""
        if self.results is None:
            raise ValueError("Execute o cálculo primeiro")
        
        lang = language or Config.LANGUAGE
        
        labels = {
            'english': {
                'title': 'Hull Resistance Analysis',
                'xlabel': 'Speed (knots)',
                'ylabel': 'Resistance (kN)',
                'total': 'Total Resistance',
                'friction': 'Frictional Resistance',
                'residual': 'Residual Resistance',
                'power': 'Effective Power (kW)'
            },
            'portuguese': {
                'title': 'Análise de Resistência do Casco',
                'xlabel': 'Velocidade (nós)',
                'ylabel': 'Resistência (kN)',
                'total': 'Resistência Total',
                'friction': 'Resistência de Atrito',
                'residual': 'Resistência Residual',
                'power': 'Potência Efetiva (kW)'
            }
        }
        
        lang_config = labels[lang]
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
        
        
        plt.subplots_adjust(
            bottom=0.095,   
            hspace=0.605     
        )
        
        # Gráfico 1: Componentes da resistência
        ax1.plot(self.results['speed_knots'], self.results['resistance_total_kN'], 
                'b-', linewidth=2.5, label=lang_config['total'])
        
        if 'resistance_friction_N' in self.results:
            ax1.plot(self.results['speed_knots'], self.results['resistance_friction_N']/1000,
                    'r--', linewidth=2, label=lang_config['friction'])
            ax1.plot(self.results['speed_knots'], self.results['residual_resistance_N']/1000,
                    'g--', linewidth=2, label=lang_config['residual'])
        
        ax1.set_xlabel(lang_config['xlabel'])
        ax1.set_ylabel(lang_config['ylabel'])
        ax1.set_title(lang_config['title'], fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Gráfico 2: Número de Froude vs Resistência
        if 'froude' in self.results:
            ax2.plot(self.results['froude'], self.results['resistance_total_kN'],
                    'purple', linewidth=2.5, marker='o', markersize=4)
            ax2.set_xlabel('Froude Number' if lang == 'english' else 'Número de Froude')
            ax2.set_ylabel(lang_config['ylabel'])
            ax2.set_title('Resistance vs Froude Number' if lang == 'english' else 'Resistência vs Número de Froude')
            ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Potência Efetiva
        if 'effective_power_kW' in self.results:
            ax3.plot(self.results['speed_knots'], self.results['effective_power_kW'],
                    'orange', linewidth=2.5, marker='s', markersize=4)
            ax3.set_xlabel(lang_config['xlabel'])
            ax3.set_ylabel(lang_config['power'])
            ax3.set_title('Effective Power' if lang == 'english' else 'Potência Efetiva')
            ax3.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Gráfico salvo como: {save_path}")
        
        plt.show()
        return fig
    
    def print_summary(self, language: str = None):
        """Imprime resumo dos resultados"""
        if self.results is None:
            raise ValueError("Execute o cálculo primeiro")
        
        lang = language or Config.LANGUAGE
        
        if lang == 'portuguese':
            print(f"\n{' RESULTADOS DA ANÁLISE ':=^80}")
            print(f"{'Veloc (nós)':>10} {'Veloc (m/s)':>10} {'Froude':>8} {'Resist (kN)':>12} {'Potência (kW)':>15}")
            print(f"{'-'*80}")
            
            for i in range(min(10, len(self.results['speed_mps']))):
                print(f"{self.results['speed_knots'][i]:>10.1f} "
                      f"{self.results['speed_mps'][i]:>10.2f} "
                      f"{self.results['froude'][i]:>8.3f} "
                      f"{self.results['resistance_total_kN'][i]:>12.1f} "
                      f"{self.results.get('effective_power_kW', [0]*len(self.results['speed_mps']))[i]:>15.1f}")
        else:
            print(f"\n{' ANALYSIS RESULTS ':=^80}")
            print(f"{'Speed (kts)':>10} {'Speed (m/s)':>10} {'Froude':>8} {'Resistance (kN)':>12} {'Power (kW)':>15}")
            print(f"{'-'*80}")
            
            for i in range(min(10, len(self.results['speed_mps']))):
                print(f"{self.results['speed_knots'][i]:>10.1f} "
                      f"{self.results['speed_mps'][i]:>10.2f} "
                      f"{self.results['froude'][i]:>8.3f} "
                      f"{self.results['resistance_total_kN'][i]:>12.1f} "
                      f"{self.results.get('effective_power_kW', [0]*len(self.results['speed_mps']))[i]:>15.1f}")

# --- FUNÇÕES DE INTERFACE ---
def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_float_input(prompt: str, default: float) -> float:
    """Entrada segura para números float"""
    while True:
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            return float(value) if value else default
        except ValueError:
            print("Por favor, digite um número válido.")

def get_speed_range_recommendation(hull_params: HullParameters, language: str) -> tuple:
    """Recomenda faixa de velocidade baseada no tipo de embarcação"""
    fn_max = 0.45 if hull_params.CB < 0.5 else 0.35  # Froude máximo recomendado
    v_max_mps = fn_max * np.sqrt(Config.GRAVITY * hull_params.L)
    v_max_kts = v_max_mps * 1.944
    
    v_min_kts = 2.0  # Velocidade mínima prática
    
    if language == 'portuguese':
        print(f"\n💡 Recomendação para este casco (CB={hull_params.CB:.3f}):")
        print(f"   Velocidade máxima recomendada: {v_max_kts:.1f} nós")
        print(f"   Velocidade mínima sugerida: {v_min_kts:.1f} nós")
        print(f"   Número de Froude máximo: {fn_max:.2f}")
    else:
        print(f"\n💡 Recommendation for this hull (CB={hull_params.CB:.3f}):")
        print(f"   Recommended maximum speed: {v_max_kts:.1f} knots")
        print(f"   Suggested minimum speed: {v_min_kts:.1f} knots")
        print(f"   Maximum Froude number: {fn_max:.2f}")
    
    return v_min_kts, v_max_kts

def interactive_calculator():
    """Interface interativa completa"""
    clear_screen()
    
    print("🚢 HULL RESISTANCE CALCULATOR v2.1")
    print("=" * 50)
    print("Desenvolvido por Italo Herodoto - Engenharia Naval\n")
    
    # Seleção de idioma
    lang_choice = input("Idioma/Language (p-português, e-english) [e]: ").strip().lower()
    Config.LANGUAGE = 'portuguese' if lang_choice == 'p' else 'english'
    
    if Config.LANGUAGE == 'portuguese':
        print("\n=== CALCULADORA DE RESISTÊNCIA AO AVANÇO ===")
        print("Digite os parâmetros do casco (Enter para valores padrão):")
    else:
        print("\n=== HULL RESISTANCE CALCULATOR ===")
        print("Enter hull parameters (Enter for defaults):")
    
    # Entrada de parâmetros
    L = get_float_input("Comprimento LWL (m)" if Config.LANGUAGE == 'portuguese' else "Length LWL (m)", 150.0)
    B = get_float_input("Boca (m)" if Config.LANGUAGE == 'portuguese' else "Beam (m)", 20.0)
    T = get_float_input("Calado (m)" if Config.LANGUAGE == 'portuguese' else "Draft (m)", 8.0)
    CB = get_float_input("Coeficiente de bloco CB" if Config.LANGUAGE == 'portuguese' else "Block coefficient CB", 0.70)
    
    # Criar parâmetros do casco
    try:
        hull = HullParameters(L=L, B=B, T=T, CB=CB)
    except ValueError as e:
        print(f"\n❌ {e}")
        return
    
    clear_screen()
    print(hull.summary(Config.LANGUAGE))
    
    # Recomendar faixa de velocidades
    v_min_rec, v_max_rec = get_speed_range_recommendation(hull, Config.LANGUAGE)
    
    # Configurar análise
    if Config.LANGUAGE == 'portuguese':
        print("\nCONFIGURAÇÃO DA ANÁLISE:")
        print("💡 Dica: Use mais pontos para curvas mais suaves (20-50 pontos)")
        min_speed = get_float_input("Velocidade mínima (nós)", max(2.0, v_min_rec))
        max_speed = get_float_input("Velocidade máxima (nós)", min(30.0, v_max_rec))
        num_points = int(get_float_input("Número de pontos (20-50 recomendado)", 30))
    else:
        print("\nANALYSIS SETUP:")
        print("💡 Tip: Use more points for smoother curves (20-50 points)")
        min_speed = get_float_input("Minimum speed (knots)", max(2.0, v_min_rec))
        max_speed = get_float_input("Maximum speed (knots)", min(30.0, v_max_rec))
        num_points = int(get_float_input("Number of points (20-50 recommended)", 30))
    
    speeds_knots = np.linspace(min_speed, max_speed, num_points)
    speeds_mps = speeds_knots / 1.944
    
    # Selecionar método
    if Config.LANGUAGE == 'portuguese':
        print("\n💡 Método Holtrop é mais preciso para navios mercantes")
        print("💡 Método Simples é mais rápido para estimativas iniciais")
        method = input("Método (1-Holtrop, 2-Simples) [1]: ").strip() or "1"
    else:
        print("\n💡 Holtrop method is more accurate for merchant ships")
        print("💡 Simple method is faster for initial estimates")
        method = input("Method (1-Holtrop, 2-Simple) [1]: ").strip() or "1"
    
    # Calcular resistência
    calculator = ResistanceCalculator(hull)
    
    if method == "1":
        results = calculator.calculate_holtrop(speeds_mps)
        method_name = "Holtrop & Mennen" if Config.LANGUAGE == 'english' else "Holtrop & Mennen"
    else:
        results = calculator.calculate_simple(speeds_mps)
        method_name = "Simple" if Config.LANGUAGE == 'english' else "Simplificado"
    
    clear_screen()
    print(f"{' ANÁLISE COMPLETA ' if Config.LANGUAGE == 'portuguese' else ' ANALYSIS COMPLETE ':=^80}")
    print(f"Método: {method_name}")
    calculator.print_summary(Config.LANGUAGE)
    
    # Estatísticas resumidas
    max_resistance = np.max(results['resistance_total_kN'])
    max_power = np.max(results.get('effective_power_kW', [0]))
    max_speed = np.max(results['speed_knots'])
    
    if Config.LANGUAGE == 'portuguese':
        print(f"\n ESTATÍSTICAS:")
        print(f"   Resistência máxima: {max_resistance:.1f} kN a {max_speed:.1f} nós")
        print(f"   Potência máxima: {max_power:.1f} kW")
        print(f"   Faixa de Froude: {np.min(results['froude']):.3f} - {np.max(results['froude']):.3f}")
    else:
        print(f"\n STATISTICS:")
        print(f"   Maximum resistance: {max_resistance:.1f} kN at {max_speed:.1f} knots")
        print(f"   Maximum power: {max_power:.1f} kW")
        print(f"   Froude range: {np.min(results['froude']):.3f} - {np.max(results['froude']):.3f}")
    
    # Exportar resultados
    if Config.LANGUAGE == 'portuguese':
        export = input("\n Exportar resultados para CSV? (s/n) [s]: ").strip().lower() or "s"
    else:
        export = input("\n Export results to CSV? (y/n) [y]: ").strip().lower() or "y"
    
    if export in ['s', 'y', 'sim', 'yes']:
        csv_file = calculator.export_results()
        if Config.LANGUAGE == 'portuguese':
            print(f" Resultados exportados: {csv_file}")
        else:
            print(f" Results exported: {csv_file}")
    
    # Gerar gráficos
    if Config.LANGUAGE == 'portuguese':
        plot = input("\n Gerar gráficos? (s/n) [s]: ").strip().lower() or "s"
    else:
        plot = input("\n Generate plots? (y/n) [y]: ").strip().lower() or "y"
    
    if plot in ['s', 'y', 'sim', 'yes']:
        calculator.plot_results(language=Config.LANGUAGE)
    
    if Config.LANGUAGE == 'portuguese':
        print("\n Análise concluída com sucesso!")
        print("💡 Dica: Consulte o README.md para interpretação dos resultados")
    else:
        print("\n Analysis completed successfully!")
        print("💡 Tip: Check README.md for results interpretation")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    try:
        interactive_calculator()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"\n Erro: {e}")
        print("Por favor, verifique os parâmetros de entrada.")
    finally:
        if Config.LANGUAGE == 'portuguese':
            print("\nObrigado por usar a Calculadora de Resistência!")
        else:
            print("\nThank you for using the Resistance Calculator!")
