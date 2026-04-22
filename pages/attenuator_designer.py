import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import textwrap

TOPOLOGIES = ["T-Pad", "Pi-Pad", "Bridged-T Pad"]

TRACE_MAG_COLOR = "#0891b2"
TRACE_RL_COLOR = "#f97316"


class AttenuatorDesigner:
    """RF Attenuator (Pad) designer with component value calculation and S-parameter plots."""

    def run(self):
        st.title("🧮 Attenuator Pad Designer")

        st.info("""
        **Quick Guide**
        - Select a **Topology**, set the desired **Attenuation**, and the **Attenuator Z₀**.
        - Specify **Source** and **Load** impedances independently to see mismatch effects.
        - Component values will be calculated and displayed.
        - S-parameter plots verify performance (S₂₁ Gain and S₁₁ Return Loss).
        """)

        # --- Configuration ---
        st.markdown("##### Configuration")
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
        with c1:
            topology = st.selectbox("Topology", TOPOLOGIES, index=0)
        with c2:
            attenuation_db = st.number_input("Attenuation (dB)", value=10.0, min_value=0.1, max_value=60.0, step=1.0)
        with c3:
            characteristic_impedance_z0 = st.number_input("Attenuator Z₀ (Ω)", value=50.0, min_value=1.0, step=10.0)
        with c4:
            source_impedance_zs = st.number_input("Source Zs (Ω)", value=50.0, min_value=1.0, step=10.0)
        with c5:
            load_impedance_zl = st.number_input("Load ZL (Ω)", value=50.0, min_value=1.0, step=10.0)

        # --- Calculations ---
        K = 10**(attenuation_db / 20)

        try:
            if topology == "T-Pad":
                R1 = characteristic_impedance_z0 * (K - 1) / (K + 1)
                R2 = 2 * characteristic_impedance_z0 * K / (K**2 - 1)
                resistor_values = {"R1": R1, "R2": R2}
            elif topology == "Pi-Pad":
                R1 = characteristic_impedance_z0 * (K + 1) / (K - 1) 
                R2 = characteristic_impedance_z0 * (K**2 - 1) / (2 * K)
                resistor_values = {"R1": R1, "R2": R2}
            elif topology == "Bridged-T Pad":
                R1 = characteristic_impedance_z0
                R2 = characteristic_impedance_z0 / (K - 1)
                R3 = characteristic_impedance_z0 * (K - 1)
                resistor_values = {"R1": R1, "R2": R2, "R3": R3}
            else:
                st.error("Unknown topology.")
                st.stop()
            
            # Calculate ABCD matrix for a matched symmetric attenuator with Z0 and K
            A = (K**2 + 1) / (2 * K)
            B = characteristic_impedance_z0 * (K**2 - 1) / (2 * K)
            C = (1 / characteristic_impedance_z0) * (K**2 - 1) / (2 * K)
            D = A
            
            S11, S21, S22 = self._abcd_to_s_params(A, B, C, D, source_impedance_zs, load_impedance_zl)

            s11_db_actual = 20 * np.log10(np.abs(S11))
            s21_db_actual = 20 * np.log10(np.abs(S21))

        except Exception as e:
            st.error(f"Calculation Error: {e}. Please check your inputs.")
            st.stop()

        # --- Display Component Values ---
        st.markdown("##### Component Values")
        cols = st.columns(len(resistor_values))
        for i, (key, value) in enumerate(resistor_values.items()):
            with cols[i]:
                label = key
                if topology == "T-Pad":
                    label = "R1 (Series)" if key == "R1" else "R2 (Shunt)"
                elif topology == "Pi-Pad":
                    label = "R1 (Shunt)" if key == "R1" else "R2 (Series)"
                elif topology == "Bridged-T Pad":
                    if key == "R1": label = "R1 (Series)"
                    elif key == "R2": label = "R2 (Shunt)"
                    elif key == "R3": label = "R3 (Bridge)"
                st.metric(label, f"{value:.2f} Ω")

        # --- Diagrams ---
        st.markdown("---")
        st.subheader("Implementation Schematic")
        if topology == "T-Pad":
            st.components.v1.html(self._t_pad_svg(resistor_values, source_impedance_zs, load_impedance_zl), height=170)
        elif topology == "Pi-Pad":
            st.components.v1.html(self._pi_pad_svg(resistor_values, source_impedance_zs, load_impedance_zl), height=170)
        elif topology == "Bridged-T Pad":
            st.components.v1.html(self._bridged_t_pad_svg(resistor_values, source_impedance_zs, load_impedance_zl), height=200)

        # --- S-Parameter Plots ---
        st.markdown("---")
        st.markdown("##### S-Parameter Plots")
        freq_axis_mhz = np.linspace(0, 1000, 100) # 0 MHz to 1 GHz for plotting (linear axis)

        # S21 (Magnitude)
        fig_s21 = go.Figure()
        fig_s21.add_trace(go.Scatter(
            x=freq_axis_mhz,
            y=np.full_like(freq_axis_mhz, s21_db_actual),
            mode='lines',
            name='S21 Magnitude',
            line=dict(color=TRACE_MAG_COLOR, width=2)
        ))
        fig_s21.update_layout(
            title="S₂₁ Transmission Coefficient",
            xaxis_title="Frequency (MHz)",
            yaxis_title="S₂₁ (dB)",
            yaxis_range=[s21_db_actual - 5, 0],
            height=380,
            template="plotly_dark"
        )
        st.plotly_chart(fig_s21, use_container_width=True)

        # S11 (Return Loss)
        fig_s11 = go.Figure()
        fig_s11.add_trace(go.Scatter(
            x=freq_axis_mhz,
            y=np.full_like(freq_axis_mhz, s11_db_actual),
            mode='lines',
            name='S11 Return Loss',
            line=dict(color=TRACE_RL_COLOR, width=2)
        ))
        fig_s11.update_layout(
            title="S₁₁ Input Reflection",
            xaxis_title="Frequency (MHz)",
            yaxis_title="S₁₁ (dB)",
            yaxis_range=[-80, 0],
            height=380,
            template="plotly_dark"
        )
        st.plotly_chart(fig_s11, use_container_width=True)

    # ==========================================================================
    # S-parameter calculations
    # ==========================================================================
    def _abcd_to_s_params(self, A, B, C, D, Zs, ZL):
        Zs = float(Zs)
        ZL = float(ZL)
        if Zs <= 0 or ZL <= 0:
            return complex(1,0), complex(0,0), complex(1,0)
        sqrt_zs_zl = math.sqrt(Zs * ZL)
        denom = A * ZL + B + C * Zs * ZL + D * Zs
        if abs(denom) < 1e-12:
            return complex(1,0), complex(0,0), complex(1,0)
        S11 = (A * ZL + B - C * Zs * ZL - D * Zs) / denom
        S21 = (2 * sqrt_zs_zl) / denom
        S22 = (A * Zs + B - C * Zs * ZL - D * ZL) / denom
        return S11, S21, S22

    # ==========================================================================
    # SVG Diagrams
    # ==========================================================================
    RESISTOR_COLOR = "#f97316"

    def _fmt_resistor_value(self, value):
        if value >= 1e3:
            return f"{value / 1e3:.1f} kΩ"
        return f"{value:.1f} Ω"

    def _t_pad_svg(self, values, zs, zl):
        r1_val = self._fmt_resistor_value(values.get("R1", 0))
        r2_val = self._fmt_resistor_value(values.get("R2", 0))
        return textwrap.dedent(f"""
        <svg width="100%" height="150" viewBox="0 0 600 150" xmlns="http://www.w3.org/2000/svg" style="background:#111; border-radius:8px; display:block; margin:auto;">
            <text x="20" y="30" fill="#888" font-size="12" font-weight="bold">T-PAD ATTENUATOR</text>
            <text x="10" y="75" fill="#fff" font-size="14">IN</text>
            <text x="570" y="75" fill="#fff" font-size="14">OUT</text>
            <text x="40" y="95" text-anchor="middle" fill="#888" font-size="10">Zs={zs:.0f}Ω</text>
            <text x="560" y="95" text-anchor="middle" fill="#888" font-size="10">ZL={zl:.0f}Ω</text>
            <line x1="60" y1="70" x2="150" y2="70" stroke="#fff" stroke-width="2"/>
            <line x1="250" y1="70" x2="350" y2="70" stroke="#fff" stroke-width="2"/>
            <line x1="450" y1="70" x2="540" y2="70" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(150, 70, 100, 0, r1_val)}
            <line x1="300" y1="70" x2="300" y2="100" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(300, 100, 0, 30, r2_val)}
            {self._draw_ground(300, 130)}
            {self._draw_resistor(350, 70, 100, 0, r1_val)}
        </svg>
        """).strip()

    def _pi_pad_svg(self, values, zs, zl):
        r1_val = self._fmt_resistor_value(values.get("R1", 0))
        r2_val = self._fmt_resistor_value(values.get("R2", 0))
        return textwrap.dedent(f"""
        <svg width="100%" height="150" viewBox="0 0 600 150" xmlns="http://www.w3.org/2000/svg" style="background:#111; border-radius:8px; display:block; margin:auto;">
            <text x="20" y="30" fill="#888" font-size="12" font-weight="bold">PI-PAD ATTENUATOR</text>
            <text x="10" y="75" fill="#fff" font-size="14">IN</text>
            <text x="570" y="75" fill="#fff" font-size="14">OUT</text>
            <text x="40" y="95" text-anchor="middle" fill="#888" font-size="10">Zs={zs:.0f}Ω</text>
            <text x="560" y="95" text-anchor="middle" fill="#888" font-size="10">ZL={zl:.0f}Ω</text>
            <line x1="60" y1="70" x2="150" y2="70" stroke="#fff" stroke-width="2"/>
            <line x1="450" y1="70" x2="540" y2="70" stroke="#fff" stroke-width="2"/>
            <line x1="150" y1="70" x2="150" y2="100" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(150, 100, 0, 30, r1_val)}
            {self._draw_ground(150, 130)}
            {self._draw_resistor(150, 70, 300, 0, r2_val)}
            <line x1="450" y1="70" x2="450" y2="100" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(450, 100, 0, 30, r1_val)}
            {self._draw_ground(450, 130)}
        </svg>
        """).strip()

    def _bridged_t_pad_svg(self, values, zs, zl):
        r1_val = self._fmt_resistor_value(values.get("R1", 0))
        r2_val = self._fmt_resistor_value(values.get("R2", 0))
        r3_val = self._fmt_resistor_value(values.get("R3", 0))
        return textwrap.dedent(f"""
        <svg width="100%" height="180" viewBox="0 0 600 180" xmlns="http://www.w3.org/2000/svg" style="background:#111; border-radius:8px; display:block; margin:auto;">
            <text x="20" y="30" fill="#888" font-size="12" font-weight="bold">BRIDGED-T PAD ATTENUATOR</text>
            <text x="10" y="75" fill="#fff" font-size="14">IN</text>
            <text x="570" y="75" fill="#fff" font-size="14">OUT</text>
            <text x="40" y="95" text-anchor="middle" fill="#888" font-size="10">Zs={zs:.0f}Ω</text>
            <text x="560" y="95" text-anchor="middle" fill="#888" font-size="10">ZL={zl:.0f}Ω</text>
            <line x1="60" y1="70" x2="150" y2="70" stroke="#fff" stroke-width="2"/>
            <line x1="250" y1="70" x2="350" y2="70" stroke="#fff" stroke-width="2"/>
            <line x1="450" y1="70" x2="540" y2="70" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(150, 70, 100, 0, r1_val)}
            <line x1="300" y1="70" x2="300" y2="100" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(300, 100, 0, 30, r2_val)}
            {self._draw_ground(300, 130)}
            <line x1="150" y1="70" x2="150" y2="40" stroke="#fff" stroke-width="2"/>
            <line x1="450" y1="70" x2="450" y2="40" stroke="#fff" stroke-width="2"/>
            {self._draw_resistor(150, 40, 300, 0, r3_val)}
            {self._draw_resistor(350, 70, 100, 0, r1_val)}
        </svg>
        """).strip()

    @staticmethod
    def _draw_resistor(x, y, length, height, label):
        """Draws a resistor symbol and its label."""
        # Resistor zig-zag path
        if length > 0: # Horizontal
            path = f"M {x},{y} "
            seg_len = length / 6
            for i in range(6):
                path += f"l {seg_len/2},{(-1 if i%2==0 else 1)*5} "
                path += f"l {seg_len/2},{(-1 if i%2==0 else 1)*-5} "
            text_x = x + length / 2
            text_y = y - 15
        else: # Vertical
            path = f"M {x},{y} "
            seg_len = height / 6
            for i in range(6):
                path += f"l {(-1 if i%2==0 else 1)*5},{seg_len/2} "
                path += f"l {(-1 if i%2==0 else 1)*-5},{seg_len/2} "
            text_x = x + 25
            text_y = y + height / 2

        return (f'<path d="{path}" fill="none" stroke="{AttenuatorDesigner.RESISTOR_COLOR}" stroke-width="2"/>'
                f'<text x="{text_x}" y="{text_y}" text-anchor="middle" fill="{AttenuatorDesigner.RESISTOR_COLOR}" font-size="11">{label}</text>')

    @staticmethod
    def _draw_ground(x, y):
        return (f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+5}" stroke="#fff" stroke-width="2"/>'
                f'<line x1="{x-10}" y1="{y+5}" x2="{x+10}" y2="{y+5}" stroke="#fff" stroke-width="1.8" opacity="0.7"/>'
                f'<line x1="{x-6}" y1="{y+9}" x2="{x+6}" y2="{y+9}" stroke="#fff" stroke-width="1.8" opacity="0.7"/>'
                f'<line x1="{x-3}" y1="{y+13}" x2="{x+3}" y2="{y+13}" stroke="#fff" stroke-width="1.8" opacity="0.7"/>')


if __name__ == "__main__":
    AttenuatorDesigner().run()