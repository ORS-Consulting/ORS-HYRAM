import streamlit as st
import hyram.phys.api as phys_api
import numpy as np
from hyram.phys import Orifice, Flame, Jet
import matplotlib.pyplot as plt
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="HyRAM Hydrogen Jet Plume Analysis", page_icon="🔥", layout="wide"
)

st.title("🔥 HyRAM Hydrogen Jet Plume Analysis")
st.markdown(
    "Interactive tool for hydrogen release and jet plume analysis using HyRAM physics models"
)

# Sidebar for parameters
st.sidebar.header("Configuration Parameters")

# Release fluid parameters
st.sidebar.subheader("Release Fluid Conditions")
release_temp = st.sidebar.number_input(
    "Temperature (K)", min_value=200.0, max_value=800.0, value=288.0, step=1.0
)
release_pres = st.sidebar.number_input(
    "Pressure (Pa)", min_value=1e5, max_value=100e6, value=35e6, step=1e6, format="%.0e"
)
release_fluid_type = st.sidebar.selectbox("Fluid Type", ["H2", "CH4", "NH3"], index=0)

# Ambient fluid parameters
st.sidebar.subheader("Ambient Conditions")
ambient_temp = st.sidebar.number_input(
    "Ambient Temperature (K)", min_value=200.0, max_value=400.0, value=288.0, step=1.0
)
ambient_pres = st.sidebar.number_input(
    "Ambient Pressure (Pa)",
    min_value=80000.0,
    max_value=120000.0,
    value=101325.0,
    step=1000.0,
)

# Leak parameters
st.sidebar.subheader("Leak Characteristics")
leak_diam = st.sidebar.number_input(
    "Leak Diameter (m)",
    min_value=0.001,
    max_value=0.1,
    value=0.003,
    step=0.001,
    format="%.3f",
)
rel_angle = st.sidebar.slider(
    "Release Angle (degrees)", min_value=0, max_value=90, value=0, step=15
)
dis_coeff = st.sidebar.number_input(
    "Discharge Coefficient", min_value=0.1, max_value=2.0, value=1.0, step=0.1
)

# Nozzle model
st.sidebar.subheader("Nozzle Model")
nozzle_model = st.sidebar.selectbox("Nozzle Model", ["yuce", "ewan", "molkov"], index=0)

# Plot parameters
st.sidebar.subheader("Plot Configuration")
create_plot = st.sidebar.checkbox("Create Concentration Plot", value=True)
vmin = st.sidebar.number_input(
    "Minimum Concentration",
    min_value=0.0,
    max_value=0.5,
    value=0.0,
    step=0.01,
    format="%.3f",
)
vmax = st.sidebar.number_input(
    "Maximum Concentration",
    min_value=0.01,
    max_value=1.0,
    value=0.1,
    step=0.01,
    format="%.3f",
)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Analysis Results")

    # Run analysis button
    if st.button("Run Analysis", type="primary"):
        try:
            with st.spinner("Running HyRAM analysis..."):
                # Create fluids
                release_fluid = phys_api.create_fluid(
                    release_fluid_type,
                    temp=release_temp,
                    pres=release_pres,
                    phase="none",
                )

                ambient_fluid = phys_api.create_fluid(
                    "AIR", temp=ambient_temp, pres=ambient_pres
                )

                # Create orifice and flame objects
                orifice = Orifice(leak_diam)
                flame = Flame(release_fluid, orifice, ambient_fluid, verbose=False)

                # Convert angle to radians
                rel_angle_rad = rel_angle * np.pi / 180

                # Run jet plume analysis
                result = phys_api.analyze_jet_plume(
                    ambient_fluid,
                    release_fluid,
                    leak_diam,
                    mass_flow=None,
                    rel_angle=rel_angle_rad,
                    dis_coeff=dis_coeff,
                    nozzle_model=nozzle_model,
                    create_plot=create_plot,
                    contours=None,
                    xmin=None,
                    xmax=None,
                    ymin=None,
                    ymax=None,
                    vmin=vmin,
                    vmax=vmax,
                    plot_title=f"{release_fluid_type} Jet Plume - Mole Fraction",
                    filename=None,
                    output_dir=None,
                    verbose=False,
                )

                # Display results
                st.success("Analysis completed successfully!")

                # Show key results
                st.subheader("Key Results")
                if (
                    hasattr(result, "mass_flow_rate")
                    and result.mass_flow_rate is not None
                ):
                    st.metric("Mass Flow Rate", f"{result.mass_flow_rate:.4f} kg/s")

                if hasattr(result, "jet") and result.jet is not None:
                    jet = result.jet
                    if hasattr(jet, "x") and len(jet.x) > 0:
                        st.metric("Maximum Jet Distance", f"{max(jet.x):.2f} m")

                # Display flame characteristics if available
                st.subheader("Flame Characteristics")
                try:
                    flame_length = flame.get_flame_length()
                    st.metric("Flame Length", f"{flame_length:.2f} m")
                except:
                    st.info("Flame length calculation not available")

                try:
                    flame_width = flame.get_flame_width()
                    st.metric("Flame Width", f"{flame_width:.2f} m")
                except:
                    st.info("Flame width calculation not available")

                # Display plot if created
                if create_plot and hasattr(result, "plot") and result.plot is not None:
                    st.subheader("Concentration Contour Plot")
                    st.pyplot(result.plot)
                elif create_plot:
                    st.info("Plot was requested but not generated by HyRAM")

        except Exception as e:
            st.error(f"Error running analysis: {str(e)}")
            st.error("Please check your HyRAM installation and parameter values")

with col2:
    st.header("Parameter Summary")

    # Display current parameters
    st.subheader("Release Conditions")
    st.write(f"**Fluid:** {release_fluid_type}")
    st.write(f"**Temperature:** {release_temp} K")
    st.write(f"**Pressure:** {release_pres:.0e} Pa")

    st.subheader("Ambient Conditions")
    st.write(f"**Temperature:** {ambient_temp} K")
    st.write(f"**Pressure:** {ambient_pres:.0f} Pa")

    st.subheader("Leak Parameters")
    st.write(f"**Diameter:** {leak_diam:.3f} m")
    st.write(f"**Angle:** {rel_angle}°")
    st.write(f"**Discharge Coeff:** {dis_coeff}")
    st.write(f"**Nozzle Model:** {nozzle_model}")

# Information section
st.markdown("---")
st.header("About HyRAM")
st.markdown(
    """
**HyRAM (Hydrogen Risk Assessment Models)** is a software toolkit for conducting quantitative risk assessments 
of hydrogen systems. This application provides an interactive interface for:

- **Jet Plume Analysis**: Modeling the dispersion of hydrogen releases
- **Flame Characteristics**: Calculating flame dimensions and properties  
- **Concentration Mapping**: Visualizing hydrogen concentration contours
- **Risk Assessment**: Supporting safety analysis of hydrogen systems

### Key Features:
- Multiple nozzle models (Yuce, Ewan, Molkov)
- Configurable release conditions and ambient parameters
- Real-time visualization of concentration contours
- Comprehensive flame characteristic calculations

### Usage Notes:
- Ensure HyRAM is properly installed with all dependencies
- Higher pressures typically result in longer jet distances
- Different nozzle models may yield varying results
- Consider meteorological conditions for realistic scenarios
"""
)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and HyRAM - For hydrogen safety analysis*")
