import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import pandas as pd
from faker import Faker
import random

# Load environment variables
load_dotenv()

# Initialize Faker for synthetic data
fake = Faker()

# Page configuration
st.set_page_config(
    page_title="Financial Forecasting - Vadis Media",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Financial Revenue Forecasting")
st.markdown("AI-powered revenue forecasting and ROI analysis for product placement opportunities.")

# Initialize session state
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Forecast Parameters")
    
    genre = st.selectbox(
        "Movie Genre",
        ["Action", "Comedy", "Drama", "Thriller", "Romance", "Sci-Fi", "Horror", "Crime", "Children's"],
        help="Select the movie genre"
    )
    
    budget_range = st.select_slider(
        "Production Budget",
        options=["< $1M", "$1M-$5M", "$5M-$20M", "$20M-$50M", "$50M-$100M", "$100M+"],
        value="$5M-$20M"
    )
    
    target_market = st.multiselect(
        "Target Markets",
        ["North America", "Europe", "Asia", "Latin America", "Middle East", "Africa", "Oceania"],
        default=["North America", "Europe"]
    )
    
    product_category = st.selectbox(
        "Product Category",
        ["Technology", "Automotive", "Fashion", "Food & Beverage", "Consumer Electronics", 
         "Luxury Goods", "Sports Equipment", "Travel", "Entertainment", "Health & Beauty"],
        help="Primary product placement category"
    )
    
    placement_count = st.slider(
        "Number of Placements",
        min_value=1,
        max_value=20,
        value=5,
        help="Estimated number of product placements"
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Analysis Options")
    
    use_real_data = st.checkbox("Use Tavily Search for Real Data", value=False)
    include_risk_analysis = st.checkbox("Include Risk Analysis", value=True)
    include_market_trends = st.checkbox("Include Market Trends", value=True)

# Main content
tab1, tab2, tab3 = st.tabs(["📈 Revenue Forecast", "🎯 ROI Analysis", "📊 Market Insights"])

with tab1:
    st.markdown("### Revenue Forecasting Model")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Forecast Parameters")
        
        expected_audience = st.number_input(
            "Expected Audience (millions)",
            min_value=0.1,
            max_value=1000.0,
            value=10.0,
            step=0.5,
            help="Projected audience size in millions"
        )
        
        avg_ticket_price = st.number_input(
            "Average Ticket Price ($)",
            min_value=5.0,
            max_value=50.0,
            value=12.0,
            step=0.5
        )
        
        placement_fee_per_product = st.number_input(
            "Avg Placement Fee per Product ($K)",
            min_value=10,
            max_value=5000,
            value=250,
            step=50,
            help="Average fee per product placement in thousands"
        )
    
    with col2:
        st.markdown("#### Quick Metrics")
        
        box_office_estimate = expected_audience * avg_ticket_price * 1_000_000
        placement_revenue = placement_count * placement_fee_per_product * 1000
        
        st.metric("Est. Box Office", f"${box_office_estimate/1_000_000:.1f}M")
        st.metric("Placement Revenue", f"${placement_revenue/1_000_000:.2f}M")
        st.metric("Total Revenue", f"${(box_office_estimate + placement_revenue)/1_000_000:.1f}M")
    
    # Generate forecast button
    if st.button("🚀 Generate Detailed Forecast", type="primary", use_container_width=True):
        with st.spinner("📊 Generating comprehensive forecast..."):
            try:
                # Generate synthetic forecast data
                forecast_data = {
                    'Genre': genre,
                    'Budget Range': budget_range,
                    'Product Category': product_category,
                    'Markets': ', '.join(target_market),
                    'Placement Count': placement_count,
                    'Expected Audience (M)': expected_audience,
                    'Box Office Revenue (M)': box_office_estimate / 1_000_000,
                    'Placement Revenue (M)': placement_revenue / 1_000_000,
                    'Total Revenue (M)': (box_office_estimate + placement_revenue) / 1_000_000,
                    'ROI': ((box_office_estimate + placement_revenue) / (float(budget_range.split('-')[0].replace('$', '').replace('M', '').replace('<', '').replace('+', '').strip()) * 1_000_000) - 1) * 100 if budget_range != "$100M+" else 150.0
                }
                
                st.session_state.forecast_data = forecast_data
                
                # AI-powered analysis
                if os.getenv("OPENAI_API_KEY"):
                    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
                    
                    prompt = f"""As a film industry financial analyst, provide a detailed revenue forecast analysis for:

Genre: {genre}
Budget: {budget_range}
Product Category: {product_category}
Target Markets: {', '.join(target_market)}
Placement Count: {placement_count}
Expected Audience: {expected_audience}M

Provide:
1. Revenue potential analysis
2. Risk factors
3. Market opportunities
4. Competitive landscape
5. Recommendations for maximizing ROI

Be specific and data-driven."""
                    
                    ai_analysis = llm.predict(prompt)
                    
                    st.markdown("### 🤖 AI Analysis")
                    st.markdown(ai_analysis)
                    
                    forecast_data['AI_Analysis'] = ai_analysis
                
                st.success("✅ Forecast generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
    
    # Display forecast results
    if st.session_state.forecast_data:
        st.markdown("---")
        st.markdown("### 📊 Forecast Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        data = st.session_state.forecast_data
        
        with col1:
            st.metric("Box Office", f"${data['Box Office Revenue (M)']:.1f}M")
        with col2:
            st.metric("Placement Revenue", f"${data['Placement Revenue (M)']:.2f}M")
        with col3:
            st.metric("Total Revenue", f"${data['Total Revenue (M)']:.1f}M")
        with col4:
            st.metric("Est. ROI", f"{data['ROI']:.1f}%")
        
        # Detailed breakdown
        st.markdown("### 📋 Detailed Breakdown")
        
        breakdown_df = pd.DataFrame([
            {"Metric": "Genre", "Value": data['Genre']},
            {"Metric": "Budget Range", "Value": data['Budget Range']},
            {"Metric": "Product Category", "Value": data['Product Category']},
            {"Metric": "Target Markets", "Value": data['Markets']},
            {"Metric": "Placement Count", "Value": data['Placement Count']},
            {"Metric": "Expected Audience", "Value": f"{data['Expected Audience (M)']}M"},
            {"Metric": "Box Office Revenue", "Value": f"${data['Box Office Revenue (M)']:.2f}M"},
            {"Metric": "Placement Revenue", "Value": f"${data['Placement Revenue (M)']:.2f}M"},
            {"Metric": "Total Revenue", "Value": f"${data['Total Revenue (M)']:.2f}M"},
            {"Metric": "ROI", "Value": f"{data['ROI']:.1f}%"}
        ])
        
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        
        # Save forecast
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Forecast"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scripts/forecast_{timestamp}.txt"
                
                with open(filename, 'w') as f:
                    f.write("FINANCIAL FORECAST REPORT\n")
                    f.write("="*80 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n\n")
                    
                    for key, value in data.items():
                        if key != 'AI_Analysis':
                            f.write(f"{key}: {value}\n")
                    
                    if 'AI_Analysis' in data:
                        f.write("\n" + "="*80 + "\n")
                        f.write("AI ANALYSIS\n")
                        f.write("="*80 + "\n\n")
                        f.write(data['AI_Analysis'])
                
                st.success(f"Forecast saved as: {filename}")
        
        with col2:
            # Download button
            forecast_text = "FINANCIAL FORECAST REPORT\n" + "="*80 + "\n\n"
            for key, value in data.items():
                if key != 'AI_Analysis':
                    forecast_text += f"{key}: {value}\n"
            
            if 'AI_Analysis' in data:
                forecast_text += "\n" + "="*80 + "\n"
                forecast_text += "AI ANALYSIS\n"
                forecast_text += "="*80 + "\n\n"
                forecast_text += data['AI_Analysis']
            
            st.download_button(
                label="⬇️ Download Forecast",
                data=forecast_text,
                file_name=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

with tab2:
    st.markdown("### 🎯 ROI Analysis")
    
    st.markdown("""
    Return on Investment (ROI) analysis helps determine the profitability of product placement 
    opportunities relative to production costs.
    """)
    
    # ROI Calculator
    st.markdown("#### ROI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        investment = st.number_input(
            "Total Investment ($M)",
            min_value=0.1,
            max_value=500.0,
            value=10.0,
            step=0.5,
            help="Total production and marketing investment"
        )
        
        revenue = st.number_input(
            "Expected Revenue ($M)",
            min_value=0.1,
            max_value=2000.0,
            value=25.0,
            step=1.0,
            help="Total expected revenue including box office and placements"
        )
    
    with col2:
        roi_value = ((revenue - investment) / investment) * 100
        profit = revenue - investment
        
        st.metric("ROI", f"{roi_value:.1f}%", delta=f"${profit:.1f}M profit")
        
        if roi_value > 100:
            st.success("🎉 Excellent ROI! Strong investment potential.")
        elif roi_value > 50:
            st.info("✅ Good ROI. Solid investment.")
        elif roi_value > 0:
            st.warning("⚠️ Positive but modest ROI. Consider optimization.")
        else:
            st.error("❌ Negative ROI. High risk investment.")
    
    # Scenario analysis
    st.markdown("---")
    st.markdown("#### Scenario Analysis")
    
    scenarios = {
        'Best Case': {'multiplier': 1.5, 'probability': 0.2},
        'Expected Case': {'multiplier': 1.0, 'probability': 0.6},
        'Worst Case': {'multiplier': 0.6, 'probability': 0.2}
    }
    
    scenario_data = []
    for scenario, params in scenarios.items():
        scenario_revenue = revenue * params['multiplier']
        scenario_roi = ((scenario_revenue - investment) / investment) * 100
        scenario_data.append({
            'Scenario': scenario,
            'Revenue ($M)': f"${scenario_revenue:.1f}",
            'ROI (%)': f"{scenario_roi:.1f}%",
            'Probability': f"{params['probability']*100:.0f}%"
        })
    
    scenario_df = pd.DataFrame(scenario_data)
    st.dataframe(scenario_df, use_container_width=True, hide_index=True)
    
    # Break-even analysis
    st.markdown("---")
    st.markdown("#### Break-Even Analysis")
    
    breakeven_revenue = investment
    breakeven_audience = breakeven_revenue / (avg_ticket_price / 1000)  # in millions
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Break-Even Revenue", f"${breakeven_revenue:.1f}M")
    with col2:
        st.metric("Break-Even Audience", f"{breakeven_audience:.1f}M people")

with tab3:
    st.markdown("### 📊 Market Insights")
    
    # Generate market insights
    if st.button("🔍 Generate Market Insights", type="primary", use_container_width=True):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OpenAI API key not found.")
        else:
            with st.spinner("Analyzing market trends..."):
                try:
                    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
                    
                    prompt = f"""As a market analyst, provide insights on product placement opportunities for:

Genre: {genre}
Product Category: {product_category}
Target Markets: {', '.join(target_market)}

Provide:
1. Current market trends
2. Successful case studies
3. Emerging opportunities
4. Brand-genre fit analysis
5. Audience demographics and preferences

Be specific with examples and data points."""
                    
                    insights = llm.predict(prompt)
                    
                    st.markdown("### 🎯 Market Analysis")
                    st.markdown(insights)
                    
                    # Save insights
                    if st.button("💾 Save Insights"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"scripts/market_insights_{timestamp}.txt"
                        
                        with open(filename, 'w') as f:
                            f.write("MARKET INSIGHTS REPORT\n")
                            f.write("="*80 + "\n")
                            f.write(f"Genre: {genre}\n")
                            f.write(f"Product Category: {product_category}\n")
                            f.write(f"Markets: {', '.join(target_market)}\n")
                            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("="*80 + "\n\n")
                            f.write(insights)
                        
                        st.success(f"Insights saved as: {filename}")
                
                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")
    
    # Industry benchmarks
    st.markdown("---")
    st.markdown("### 📈 Industry Benchmarks")
    
    # Generate synthetic benchmark data
    benchmark_data = []
    genres = ["Action", "Comedy", "Drama", "Thriller", "Romance"]
    
    for g in genres:
        benchmark_data.append({
            'Genre': g,
            'Avg Box Office ($M)': f"${random.randint(20, 200)}",
            'Avg Placement Revenue ($M)': f"${random.randint(1, 10)}",
            'Avg ROI (%)': f"{random.randint(50, 300)}%"
        })
    
    benchmark_df = pd.DataFrame(benchmark_data)
    st.dataframe(benchmark_df, use_container_width=True, hide_index=True)
    
    st.info("💡 **Note:** Benchmark data is for illustrative purposes. Actual results may vary based on numerous factors.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💡 Tip: Combine multiple data sources and scenarios for the most accurate forecasts.</p>
</div>
""", unsafe_allow_html=True)
