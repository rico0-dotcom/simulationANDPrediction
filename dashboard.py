import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from IPython.display import display
import matplotlib.pyplot as plt



st.title("Infosys Stock Analysis")
st.markdown("### DCF and Monte Carlo Simulation Analysis on Infosys")
#exchange = st.number_input("Enter Exchange Rate (Default: 85.26)", min_value=0.0, value=85.26, format="%.2f")

data={
        "Company":['Infosys','Wipro','TCS','HCL Tech'],
        "Market Price": [1922,305,4170,1911],
        'EPS':[63.29,20.82,125.88,57.86],
        'Market Cap':[7981280000000,3194450000000,15088510000000,5186760000000],
        'Debt':[83590000000,1646490000000,80210000000,57560000000],
        'Cash':[147860000000,969530000000,90160000000,94560000000],
        'EBITDA':[364250000000,1677580000000,642930000000,241980000000],
        'Revenue':[1536700000000, 8976030000000,2408930000000,1099130000000 ]
}



    
def calculate_terminal_value(last_fcf,terminal_growth,discount_rate):
    return last_fcf*(1+terminal_growth)/(discount_rate-terminal_growth)
    
def Calculate_dcf(fcf,wacc):
    dcf=[fcf/(1+wacc)**i for i,fcf in enumerate(fcf,1)]
    #st.write(dcf)
    return sum(dcf)


#slider
wacc=st.slider("WACC %",10.00,14.50,11.54)


st.subheader("Dcf Calculation")
forecasted_fcfs=[3095448259.1053576, 3324705039.8328905, 3570941161.5508423, 3835414157.4914017, 4119474697.0002775]
dcf=Calculate_dcf(fcf=forecasted_fcfs,wacc=wacc/100)
st.write(f'The (DCF) of Infosys over 5 year is: ${dcf:,.2f}')

growth_rate=st.slider('Growth Rate %',1.00,6.50,3.00)

st.subheader('Intrinsic value')
terminal_value=terminal_value=calculate_terminal_value(forecasted_fcfs[-1],growth_rate/100,wacc/100)
sensitivity_results=dcf+terminal_value
st.write(f'The intrinsic Value of infosys is:${sensitivity_results:,.2f}')

#peer analysis


st.title("Peer Comparison")
data['Market Price']= pd.to_numeric(data['Market Price'], errors='coerce')
data['EPS']=pd.to_numeric(data['EPS'], errors='coerce')
data['P/E Ratio'] = data['Market Price'] / data['EPS']
data['Market Cap']= pd.to_numeric(data['Market Cap'], errors='coerce')
data['Debt']= pd.to_numeric(data['Debt'], errors='coerce')
data['Cash']= pd.to_numeric(data['Cash'], errors='coerce')
data['Enterprise Value'] = data['Market Cap'] + data['Debt'] - data['Cash']
data['EV/EBITDA'] = data['Enterprise Value'] / data['EBITDA']
#display(data[['Market Price', 'P/E Ratio' ]])
data = pd.DataFrame(data)

# Sidebar Widgets
st.header("Filters and Options")
show_all = st.checkbox("Show All peer review", value=False)  # Default: False
selected_companies = st.multiselect(
    "Select Companies:", options=data['Company'], default=data['Company']
)

# Filter Data
filtered_data = data[data['Company'].isin(selected_companies)]

if not show_all:
    # Single Metric Selection
    metric = st.selectbox("Metric for Peer Comparison:", options=data.columns[1:], index=0)
    fig = px.bar(
        filtered_data,
        x='Company',
        y=metric,
        color='Company',
        title=f"Peer Comparison: {metric}",
        labels={metric: metric}
    )
    fig.update_traces(marker=dict(line=dict(color='black',width=2)),texttemplate='₹%{y:.2f}', textposition='outside')
    fig.update_layout(yaxis_tickprefix="₹")
    
    st.plotly_chart(fig)

else:
    
    st.subheader("Peer Comparison Across All Metrics")
    for metric in data.columns[1:]: 
        st.write(f"### {metric}")
        fig = px.bar(
            filtered_data,
            x='Company',
            y=metric,
            color='Company',
            title=f"{metric} Comparison",
            labels={metric: metric}
        )
        fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
        st.plotly_chart(fig)

# rawdata
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data in ₹")
    st.write(filtered_data)


st.sidebar.subheader("Metrics Summary")
st.sidebar.write(f"Average {metric}: {filtered_data[metric].mean():.2f}")
st.sidebar.write(f"Max {metric}: {filtered_data[metric].max():.2f}")
st.sidebar.write(f"Min {metric}: {filtered_data[metric].min():.2f}")




st.title("Monte Carlo Simulation for DCF with Interactive Inputs")



st.sidebar.header("Inputs for Simulation")

WACC_mean = st.sidebar.number_input("Mean WACC (%)", min_value=0.0, max_value=100.0, value=11.53, step=0.0001,format="%.4f") / 100
WACC_std = st.sidebar.number_input("WACC Std Dev (%)", min_value=0.0, max_value=100.0, value=1.154, step=0.0001,format="%.4f") / 100
Terminal_Growth_mean = st.sidebar.number_input("Mean Terminal Growth (%)", min_value=0.0, max_value=100.0, value=3.5, step=0.0001,format="%.4f") / 100
Terminal_Growth_std = st.sidebar.number_input("Terminal Growth Std Dev (%)", min_value=0.0, max_value=100.0, value=1.443, step=0.0001,format="%.4f") / 100
num_simulations = st.sidebar.slider("Number of Simulations", min_value=1000, max_value=100000, value=1000, step=1000)

# Input for forecasted free cash flows
#forecasted_fcfs = st.sidebar.text_area(
    #"Forecasted Free Cash Flows")
#forecasted_fcfs = [float(x.strip()) for x in forecasted_fcfs.split(",")]

#result
st.header("Monte Carlo Simulation Results")


simulated_values = []
for _ in range(num_simulations):
    # Sample WACC and terminal growth rate
    wacc_sample = np.random.normal(WACC_mean, WACC_std)
    growth_sample = np.random.normal(Terminal_Growth_mean, Terminal_Growth_std)

    if wacc_sample <= growth_sample:
        continue

    
    terminal_value = calculate_terminal_value(forecasted_fcfs[-1], growth_sample, wacc_sample)
    dcf_value = Calculate_dcf(forecasted_fcfs, wacc_sample) + (terminal_value / (1 + wacc_sample)**len(forecasted_fcfs))
    simulated_values.append(dcf_value)

simulated_values = np.array(simulated_values)


mean_value = np.mean(simulated_values)
percentile_5 = np.percentile(simulated_values, 5)
percentile_95 = np.percentile(simulated_values, 95)

st.write(f"**Mean DCF Value:** ${mean_value:,.2f}")
st.write(f"**5th Percentile DCF Value:** ${percentile_5:,.2f}")
st.write(f"**95th Percentile DCF Value:** ${percentile_95:,.2f}")

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(simulated_values, bins=50, alpha=0.6, color='blue')
ax.axvline(mean_value, color='red', linestyle='--', label=f"Mean Value: ${mean_value:,.2f}")
ax.axvline(percentile_5, color='green', linestyle='--', label=f"5th Percentile: ${percentile_5:,.2f}")
ax.axvline(percentile_95, color='green', linestyle='--', label=f"95th Percentile: ${percentile_95:,.2f}")
ax.set_title("Monte Carlo Simulation of DCF Values")
ax.set_xlabel("DCF Value (US Dollar)")
ax.set_ylabel("Frequency")
ax.legend()



st.pyplot(fig)
