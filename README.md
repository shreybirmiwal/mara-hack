#IGNORE DO NOT READ THIS IS OLD


# Plan Summary & Flow

1.  **User Input:** User asks a natural language question (e.g., "what if a heatwave hits Texas?").
2.  **AI Interpreter (LLM #1):** An LLM call translates the user's question into a structured JSON object (`{ "event": "heatwave", "location": "ERCOT" }`).
3.  **Backend Logic (The "Analog Engine"):**
    *   The backend receives the JSON.
    *   Based on the event and location, it knows which historical dataset to query (e.g., `ercot_temperature_forecast_by_weather_zone`).
    *   It finds a date where a similar event actually happened (e.g., finds a day with >100°F temps).
4.  **Data Retrieval:** The backend fetches all relevant data for that historical date:
    *   **Prices:** from `ercot_spp_day_ahead_hourly`.
    *   **Demand/Load:** from `ercot_load_forecast_by_weather_zone`.
    *   ...and other relevant metrics.
5.  **Simulation & Visualization:**
    *   The backend sends this data bundle to the frontend.
    *   The frontend uses the price data to color a **static GeoJSON map** of ERCOT zones.
    *   It also uses the data to draw time-series charts (price, demand, etc.).
6.  **AI Narrative (LLM #2):** The data bundle is sent to another LLM to generate a human-readable summary of the event, which is displayed to the user.



# prompt
Design an AI driven trading system that will arbitrage energy and inference marketplace prices to optimize compute allocation, while utilizing bitcoin miners and HPC servers to fulfill that demand.
Here were some of the ideas we mentioned, but not limited to


For those focused on Bitcoin, feel free to dive deeper into a few other areas:

Global hashrate and network difficulty predictions
Network analysis of transaction data
Study trends amongst bitcoin mining pools and forecast whos gonna win the next block

For those marketplace driven,
Make an entirely new marketplace
Build a derivatives / futures market for underlying assets (hashrate, bitcoin, compute)

For those AI focused,
Build an agent on top of any of these publicly available APIs (energy, bitcoin, inference compute)

For those energy focused,
Study the energy markets (texas, ERCOT) to determine optimal data center usage (maximizing dollars per watt)

For those data focused:
Based off the pricing info from our API or external markets, what gaps or opportunities have you identified
Generate some dashboards or visuals to identify trends: how often did pricing work in your favor, etc.


ideas:
## p1 simulate how energy prices react
Map of all the energy prices
User enters prompt 'lets make cloudy'
Weather data
Gpt to write a query in api format
Find when it was actually cloudy get the date and time
Cross reference with energy price then and their
Call gpt again to RAG that data combine with user prompt to create new reality
Display the new simulated changes


## p2: simulate how miners react
above only explains energy price
We need another model for energy price → how miners should react


## p3: simulate how humans react





## all the datasets we have access to
ISONE
Zonal Load Real Time Hourly	isone_zonal_load_real_time_hourly	06/30/2017	06/21/2025, 10:08 AM PDT
MISO
Zonal Load Hourly	miso_zonal_load_hourly	05/31/2013	06/21/2025, 10:07 AM PDT
NYISO
Zonal Load Forecast Hourly	nyiso_zonal_load_forecast_hourly	04/19/2000	06/21/2025, 10:07 AM PDT
IESO
Zonal Load Forecast (Pre-Market Renewal)	ieso_zonal_load_forecast_hourly_pre_market_renewal	10/06/2023	05/17/2025, 05:42 AM PDT
IESO
Zonal Load Forecast	ieso_zonal_load_forecast_hourly	05/02/2025	06/21/2025, 10:07 AM PDT
IESO
Wind Market Participant Forecast	ieso_wind_market_participant_forecast	04/11/2025	06/21/2025, 10:08 AM PDT
PJM
Wind Generation Instantaneous	pjm_wind_generation_instantaneous	06/27/2024	06/21/2025, 10:08 AM PDT
PJM
Wind Generation By Area	pjm_wind_generation_by_area	12/31/2010	06/21/2025, 10:08 AM PDT
PJM
Wind Forecast Hourly	pjm_wind_forecast_hourly	02/22/2024	06/21/2025, 10:08 AM PDT
MISO
Wind Forecast Hourly	miso_wind_forecast_hourly	06/29/2021	06/21/2025, 10:07 AM PDT
ISONE
Wind Forecast Hourly	isone_wind_forecast_hourly	01/01/2023	06/21/2025, 10:08 AM PDT
PJM
Wind Forecast 5 Min	pjm_wind_forecast_5_min	09/07/2024	06/21/2025, 10:08 AM PDT
IESO
Wind Embedded Forecast	ieso_wind_embedded_forecast	04/11/2025	06/21/2025, 10:08 AM PDT
ERCOT
Wind Actual And Forecast Hourly	ercot_wind_actual_and_forecast_hourly	12/31/2017	06/21/2025, 09:56 AM PDT
ERCOT
Wind Actual And Forecast By Geo Region Hourly	ercot_wind_actual_and_forecast_by_geo_region_hourly	10/04/2017	06/21/2025, 09:57 AM PDT
SPP
VER Curtailments	spp_ver_curtailments	02/28/2014	06/21/2025, 10:08 AM PDT
ERCOT
Unplanned Resource Outages	ercot_unplanned_resource_outages	12/06/2022	06/21/2025, 03:01 AM PDT
IESO
Transmission Outages Planned	ieso_transmission_outages_planned	04/29/2025	06/21/2025, 10:07 AM PDT
PJM
Transmission Limits	pjm_transmission_limits	06/17/2024	06/21/2025, 10:08 AM PDT
PJM
Transmission Constraints Day Ahead Hourly	pjm_transmission_constraints_day_ahead_hourly	12/31/2009	06/21/2025, 10:08 AM PDT
PJM
Transfer Interface Information 5 Min	pjm_transfer_interface_information_5_min	06/17/2024	06/21/2025, 10:08 AM PDT
CAISO
Tie Flows Real Time 5 Min	caiso_tie_flows_real_time_5_min	05/01/2021	06/21/2025, 10:08 AM PDT
CAISO
Tie Flows Real Time 15 Min	caiso_tie_flows_real_time_15_min	12/01/2021	06/21/2025, 10:08 AM PDT
PJM
Tie Flows 5 Min	pjm_tie_flows_5_min	04/23/2025	06/21/2025, 10:08 AM PDT
ERCOT
Temperature Forecast By Weather Zone	ercot_temperature_forecast_by_weather_zone	01/01/2017	06/21/2025, 03:01 AM PDT
ERCOT
System-Level Load And ESR Charging	ercot_system_load_charging_4_seconds	05/30/2025	06/21/2025, 10:08 AM PDT
MISO
Subregional Power Balance Constraints Real Time 5 Minutes	miso_subregional_power_balance_constraints_real_time_5_min	01/02/2022	06/21/2025, 10:07 AM PDT
MISO
Subregional Power Balance Constraints Day Ahead Hourly	miso_subregional_power_balance_constraints_day_ahead_hourly	01/01/2022	06/21/2025, 10:07 AM PDT
CAISO
Storage	caiso_storage	03/24/2023	06/21/2025, 10:07 AM PDT
IESO
Solar Market Participant Forecast	ieso_solar_market_participant_forecast	04/11/2025	06/21/2025, 10:08 AM PDT
PJM
Solar Generation By Area	pjm_solar_generation_by_area	12/31/2018	06/21/2025, 10:08 AM PDT
PJM
Solar Generation 5 Min	pjm_solar_generation_5_min	06/12/2024	06/21/2025, 10:08 AM PDT
PJM
Solar Forecast Hourly	pjm_solar_forecast_hourly	02/22/2024	06/21/2025, 10:08 AM PDT
MISO
Solar Forecast Hourly	miso_solar_forecast_hourly	04/29/2022	06/21/2025, 10:07 AM PDT
ISONE
Solar Forecast Hourly	isone_solar_forecast_hourly	01/01/2024	06/21/2025, 10:08 AM PDT
PJM
Solar Forecast 5 Min	pjm_solar_forecast_5_min	09/07/2024	06/21/2025, 10:08 AM PDT
IESO
Solar Embedded Forecast	ieso_solar_embedded_forecast	04/11/2025	06/21/2025, 10:07 AM PDT
SPP
Solar And Wind Forecast Short Term	spp_solar_and_wind_forecast_short_term	07/20/2017	06/21/2025, 10:08 AM PDT
SPP
Solar And Wind Forecast Mid Term	spp_solar_and_wind_forecast_mid_term	07/20/2017	06/21/2025, 10:08 AM PDT
CAISO
Solar And Wind Forecast DAM	caiso_solar_and_wind_forecast_dam	12/31/2020	06/21/2025, 10:07 AM PDT
ERCOT
Solar Actual And Forecast Hourly	ercot_solar_actual_and_forecast_hourly	09/01/2016	06/21/2025, 09:57 AM PDT
ERCOT
Solar Actual And Forecast By Geo Region Hourly	ercot_solar_actual_and_forecast_by_geo_region_hourly	06/30/2022	06/21/2025, 09:57 AM PDT
ERCOT
Short Term System Adequacy	ercot_short_term_system_adequacy	12/31/2016	06/21/2025, 10:01 AM PDT
ERCOT
Shadow Prices SCED	ercot_shadow_prices_sced	12/29/2010	06/21/2025, 10:08 AM PDT
IESO
Shadow Prices Real Time 5 Min	ieso_shadow_prices_real_time_5_min	05/07/2025	06/21/2025, 06:03 AM PDT
IESO
Shadow Prices Day Ahead Hourly	ieso_shadow_prices_day_ahead_hourly	05/09/2025	06/21/2025, 06:03 AM PDT
ERCOT
Shadow Prices DAM	ercot_shadow_prices_dam	11/30/2010	06/21/2025, 10:08 AM PDT
ISONE
Seven-Day Capacity Forecast	isone_capacity_forecast_7_day	12/31/2017	06/21/2025, 10:08 AM PDT
PJM
Settlements Verified LMP Hourly	pjm_settlements_verified_lmp_hourly	12/31/2009	06/21/2025, 10:08 AM PDT
PJM
Settlements Verified LMP 5 Min	pjm_settlements_verified_lmp_5_min	03/31/2018	06/21/2025, 10:08 AM PDT
GRIDSTATUS
SPP Records	spp_records	08/06/2019	06/21/2025, 10:06 AM PDT
ERCOT
SPP Real Time Price Corrections	ercot_spp_real_time_price_corrections	02/27/2012	06/21/2025, 08:01 AM PDT
ERCOT
SPP Real Time 15 Min	ercot_spp_real_time_15_min	11/30/2010	06/21/2025, 10:02 AM PDT
GRIDSTATUS
SPP New Records Timeline	spp_records_timeseries	12/31/2010	06/21/2025, 10:07 AM PDT
ERCOT
SPP Day Ahead Price Corrections	ercot_spp_day_ahead_price_corrections	03/07/2012	06/21/2025, 08:00 AM PDT
ERCOT
SPP Day Ahead Hourly	ercot_spp_day_ahead_hourly	11/30/2010	06/20/2025, 09:19 PM PDT
ERCOT
SCED System Lambda	ercot_sced_system_lambda	12/31/2015	06/21/2025, 10:09 AM PDT
ERCOT
SCED SMNE 60 Day	ercot_sced_smne_60_day	11/01/2018	06/21/2025, 08:07 AM PDT
ERCOT
SCED Load Resource 60 Day	ercot_sced_load_resource_60_day	11/01/2018	06/21/2025, 08:07 AM PDT
ERCOT
SCED Generation Resource 60 Day	ercot_sced_gen_resource_60_day	11/01/2018	06/21/2025, 08:07 AM PDT
ERCOT
Reported Outages	ercot_reported_outages	03/29/2024	06/21/2025, 10:08 AM PDT
CAISO
Renewables Hourly	caiso_renewables_hourly	03/01/2022	06/21/2025, 10:07 AM PDT
CAISO
Renewables Forecast RTPD	caiso_renewables_forecast_rtpd	12/31/2019	06/21/2025, 10:08 AM PDT
CAISO
Renewables Forecast RTD	caiso_renewables_forecast_rtd	12/31/2019	06/21/2025, 10:07 AM PDT
CAISO
Renewables Forecast HASP	caiso_renewables_forecast_hasp	11/30/2021	06/21/2025, 10:07 AM PDT
CAISO
Renewables Forecast DAM	caiso_renewables_forecast_dam	12/31/2020	06/21/2025, 10:07 AM PDT
ISONE
Reliability Region Load Forecast	isone_reliability_region_load_forecast	06/29/2017	06/21/2025, 10:08 AM PDT
PJM
Regulation Market Monthly	pjm_regulation_market_monthly	09/30/2012	06/21/2025, 10:08 AM PDT
EIA
Regional Hourly	eia_regional_hourly	06/30/2015	06/21/2025, 10:01 AM PDT
IESO
Real Time Totals	ieso_real_time_totals	03/31/2025	06/21/2025, 10:07 AM PDT
ERCOT
Real Time System Conditions	ercot_real_time_system_conditions	06/19/2023	06/21/2025, 10:09 AM PDT
ERCOT
Real Time Adders And Reserves	ercot_real_time_adders_and_reserves	12/31/2016	06/21/2025, 10:09 AM PDT
ERCOT
Real Time AS Monitor	ercot_real_time_as_monitor	06/15/2023	06/21/2025, 10:09 AM PDT
PJM
Projected RTO Statistics At Peak	pjm_projected_rto_statistics_at_peak	08/24/2011	06/21/2025, 10:08 AM PDT
PJM
Projected Area Statistics At Peak	pjm_projected_area_statistics_at_peak	08/24/2011	06/21/2025, 10:08 AM PDT
EIA
Preliminary Monthly Electric Generator Inventory: Retired	eia_monthly_generator_inventory_retired	02/25/2016	06/20/2025, 08:32 PM PDT
EIA
Preliminary Monthly Electric Generator Inventory: Planned	eia_monthly_generator_inventory_planned	02/25/2016	06/20/2025, 08:32 PM PDT
EIA
Preliminary Monthly Electric Generator Inventory: Operating	eia_monthly_generator_inventory_operating	02/25/2016	06/20/2025, 08:32 PM PDT
EIA
Preliminary Monthly Electric Generator Inventory: Canceled Or Postponed	eia_monthly_generator_inventory_canceled_or_postponed	02/25/2016	06/20/2025, 08:32 PM PDT
GRIDSTATUS
PJM Records	pjm_records	04/17/2023	06/21/2025, 10:06 AM PDT
GRIDSTATUS
PJM New Records Timeline	pjm_records_timeseries	04/01/2016	06/21/2025, 10:06 AM PDT
PJM
Outages Daily	pjm_outages_daily	05/25/2015	06/21/2025, 10:08 AM PDT
CAISO
Outages Aggregated Hourly	caiso_outages_aggregated_hourly	06/17/2021	06/21/2025, 08:37 AM PDT
IESO
Outage Transmission Limits	ieso_outage_transmission_limits	04/22/2025	06/21/2025, 10:07 AM PDT
PJM
Operational Reserves	pjm_operational_reserves	07/02/2024	06/21/2025, 10:08 AM PDT
SPP
Operating Reserves	spp_operating_reserves	08/28/2014	06/21/2025, 10:08 AM PDT
CAISO
Net Interchange Real Time	caiso_net_interchange_real_time	-	-
GRIDSTATUS
NYISO Records	nyiso_records	07/02/2018	06/21/2025, 10:06 AM PDT
GRIDSTATUS
NYISO New Records Timeline	nyiso_records_timeseries	01/01/2018	06/21/2025, 10:06 AM PDT
EIA
Monthly Plant Inventory Operating	eia_monthly_plant_inventory_operating	02/25/2016	05/22/2025, 08:32 PM PDT
PJM
Marginal Value Real Time 5 Min	pjm_marginal_value_real_time_5_min	03/31/2018	06/21/2025, 10:08 AM PDT
PJM
Marginal Value Day Ahead Hourly	pjm_marginal_value_day_ahead_hourly	12/31/2009	06/21/2025, 10:08 AM PDT
GRIDSTATUS
MISO Records	miso_records	04/16/2023	06/21/2025, 10:06 AM PDT
GRIDSTATUS
MISO New Records Timeline	miso_records_timeseries	12/01/2022	06/21/2025, 10:06 AM PDT
IESO
MCP Real Time 5 Min	ieso_mcp_real_time_5_min	12/31/2017	05/17/2025, 05:41 AM PDT
MISO
Look Ahead Hourly	miso_look_ahead_hourly	12/31/2021	06/21/2025, 10:07 AM PDT
IESO
Load Zonal Hourly	ieso_load_zonal_hourly	12/31/2024	06/21/2025, 10:07 AM PDT
IESO
Load Zonal 5 Min	ieso_load_zonal_5_min	12/31/2024	06/21/2025, 10:07 AM PDT
NYISO
Load Raw	nyiso_load_raw	12/31/2017	06/21/2025, 10:07 AM PDT
PJM
Load Metered Hourly	pjm_load_metered_hourly	12/31/1992	06/21/2025, 10:08 AM PDT
ISONE
Load Hourly	isone_load_hourly	06/30/2017	06/21/2025, 10:08 AM PDT
IESO
Load Hourly	ieso_load_hourly	-	-
CAISO
Load Hourly	caiso_load_hourly	10/03/2008	06/21/2025, 10:09 AM PDT
SPP
Load Forecast Mid Term	spp_load_forecast_mid_term	12/31/2013	06/21/2025, 10:08 AM PDT
MISO
Load Forecast Mid Term	miso_load_forecast_mid_term	12/31/2020	06/21/2025, 10:07 AM PDT
PJM
Load Forecast Hourly Historical	pjm_load_forecast_hourly_historical	01/01/2011	06/21/2025, 10:07 AM PDT
PJM
Load Forecast Hourly	pjm_load_forecast_hourly	06/28/2024	06/21/2025, 10:07 AM PDT
NYISO
Load Forecast Hourly	nyiso_load_forecast_hourly	04/19/2000	06/21/2025, 10:07 AM PDT
ISONE
Load Forecast Hourly	isone_load_forecast_hourly	07/31/2016	06/21/2025, 10:08 AM PDT
IESO
Load Forecast Hourly	ieso_load_forecast_hourly	01/02/2024	06/21/2025, 10:06 AM PDT
CAISO
Load Forecast Day Ahead	caiso_load_forecast_day_ahead	03/31/2009	06/21/2025, 10:09 AM PDT
CAISO
Load Forecast DAM	caiso_load_forecast_dam	03/31/2009	06/21/2025, 10:09 AM PDT
ERCOT
Load Forecast By Weather Zone	ercot_load_forecast_by_weather_zone	12/31/2015	06/21/2025, 09:30 AM PDT
ERCOT
Load Forecast By Forecast Zone	ercot_load_forecast_by_forecast_zone	12/31/2015	06/21/2025, 09:30 AM PDT
CAISO
Load Forecast 7 Day	caiso_load_forecast_7_day	03/25/2009	06/21/2025, 10:06 AM PDT
PJM
Load Forecast 5 Min	pjm_load_forecast_5_min	04/14/2025	06/21/2025, 10:08 AM PDT
CAISO
Load Forecast 5 Min	caiso_load_forecast_5_min	03/31/2009	06/21/2025, 10:09 AM PDT
CAISO
Load Forecast 2 Day	caiso_load_forecast_2_day	03/30/2009	06/21/2025, 10:09 AM PDT
CAISO
Load Forecast 15 Min	caiso_load_forecast_15_min	04/30/2014	06/21/2025, 10:09 AM PDT
SPP
Load Forecast	spp_load_forecast	04/12/2023	06/21/2025, 10:08 AM PDT
PJM
Load Forecast	pjm_load_forecast	04/12/2023	06/21/2025, 10:07 AM PDT
NYISO
Load Forecast	nyiso_load_forecast	04/11/2000	06/21/2025, 10:07 AM PDT
MISO
Load Forecast	miso_load_forecast	12/31/2020	06/21/2025, 10:07 AM PDT
ISONE
Load Forecast	isone_load_forecast	07/31/2016	06/21/2025, 10:08 AM PDT
ERCOT
Load Forecast	ercot_load_forecast	01/01/2016	06/21/2025, 09:30 AM PDT
CAISO
Load Forecast	caiso_load_forecast	03/31/2009	06/21/2025, 10:06 AM PDT
ERCOT
Load By Weather Zone	ercot_load_by_weather_zone	06/12/2013	06/21/2025, 10:08 AM PDT
ERCOT
Load By Forecast Zone	ercot_load_by_forecast_zone	06/28/2017	06/21/2025, 10:08 AM PDT
ERCOT
Load 15 Min	ercot_load_15_min	12/31/2015	06/21/2025, 10:06 AM PDT
SPP
Load	spp_load	12/31/2014	06/21/2025, 10:08 AM PDT
PJM
Load	pjm_load	02/06/2023	06/21/2025, 10:07 AM PDT
NYISO
Load	nyiso_load	12/31/2017	06/21/2025, 10:07 AM PDT
MISO
Load	miso_load	11/30/2022	06/21/2025, 10:07 AM PDT
ISONE
Load	isone_load	11/30/2020	06/21/2025, 10:08 AM PDT
IESO
Load	ieso_load	12/04/2023	06/21/2025, 10:05 AM PDT
ERCOT
Load	ercot_load	06/12/2013	06/21/2025, 10:08 AM PDT
CAISO
Load	caiso_load	04/10/2018	06/21/2025, 10:08 AM PDT
GRIDSTATUS
Latest Data For ISOs	isos_latest	-	-
NYISO
Lake Erie Circulation Real Time	nyiso_lake_erie_circulation_real_time	05/09/2009	06/21/2025, 10:05 AM PDT
NYISO
Lake Erie Circulation Day Ahead	nyiso_lake_erie_circulation_day_ahead	05/09/2009	06/21/2025, 06:35 AM PDT
ERCOT
LMP With Adders By Settlement Point	ercot_lmp_with_adders_by_settlement_point	-	-
CAISO
LMP Scheduling Point Tie Real Time 5 Min	caiso_lmp_scheduling_point_tie_real_time_5_min	01/01/2020	06/21/2025, 10:08 AM PDT
CAISO
LMP Scheduling Point Tie Real Time 15 Min	caiso_lmp_scheduling_point_tie_real_time_15_min	06/20/2019	06/21/2025, 10:08 AM PDT
CAISO
LMP Scheduling Point Tie Day Ahead Hourly	caiso_lmp_scheduling_point_tie_day_ahead_hourly	01/31/2019	06/21/2025, 10:08 AM PDT
SPP
LMP Real Time WEIS	spp_lmp_real_time_weis	12/31/2021	06/21/2025, 10:08 AM PDT
PJM
LMP Real Time Unverified Hourly	pjm_lmp_real_time_unverified_hourly	03/18/2025	06/21/2025, 10:08 AM PDT
IESO
LMP Real Time Operating Reserves	ieso_lmp_real_time_operating_reserves	04/30/2025	06/21/2025, 10:07 AM PDT
MISO
LMP Real Time Hourly Prelim	miso_lmp_real_time_hourly_prelim	06/29/2024	06/21/2025, 04:20 AM PDT
ISONE
LMP Real Time Hourly Prelim	isone_lmp_real_time_hourly_prelim	06/30/2017	06/21/2025, 10:08 AM PDT
MISO
LMP Real Time Hourly Final	miso_lmp_real_time_hourly_final	09/30/2021	06/21/2025, 04:21 AM PDT
ISONE
LMP Real Time Hourly Final	isone_lmp_real_time_hourly_final	06/30/2017	06/21/2025, 10:08 AM PDT
MISO
LMP Real Time Hourly Ex Post Prelim	miso_lmp_real_time_hourly_ex_post_prelim	06/29/2024	06/21/2025, 10:05 AM PDT
MISO
LMP Real Time Hourly Ex Post Final	miso_lmp_real_time_hourly_ex_post_final	03/24/2016	06/21/2025, 03:32 AM PDT
PJM
LMP Real Time Hourly	pjm_lmp_real_time_hourly	12/31/2009	06/21/2025, 10:08 AM PDT
SPP
LMP Real Time By Bus	spp_lmp_real_time_by_bus	12/31/2020	06/21/2025, 10:08 AM PDT
IESO
LMP Real Time 5 Min Virtual Zonal	ieso_lmp_real_time_5_min_virtual_zonal	05/01/2025	06/21/2025, 10:07 AM PDT
ISONE
LMP Real Time 5 Min Prelim	isone_lmp_real_time_5_min_prelim	06/30/2022	06/21/2025, 10:08 AM PDT
IESO
LMP Real Time 5 Min Ontario Zonal	ieso_lmp_real_time_5_min_ontario_zonal	05/01/2025	06/21/2025, 10:07 AM PDT
IESO
LMP Real Time 5 Min Intertie	ieso_lmp_real_time_5_min_intertie	05/01/2025	06/21/2025, 10:07 AM PDT
MISO
LMP Real Time 5 Min Final	miso_lmp_real_time_5_min_final	12/19/2021	06/16/2025, 09:02 AM PDT
ISONE
LMP Real Time 5 Min Final	isone_lmp_real_time_5_min_final	06/30/2022	06/21/2025, 10:08 AM PDT
MISO
LMP Real Time 5 Min Ex Post Prelim	miso_lmp_real_time_5_min_ex_post_prelim	03/24/2023	06/21/2025, 10:05 AM PDT
MISO
LMP Real Time 5 Min Ex Post Final	miso_lmp_real_time_5_min_ex_post_final	12/31/2019	06/21/2025, 03:43 AM PDT
MISO
LMP Real Time 5 Min Ex Ante	miso_lmp_real_time_5_min_ex_ante	12/07/2024	06/21/2025, 03:33 AM PDT
IESO
LMP Real Time 5 Min All	ieso_lmp_real_time_5_min_all	-	-
SPP
LMP Real Time 5 Min	spp_lmp_real_time_5_min	05/29/2013	06/21/2025, 10:08 AM PDT
PJM
LMP Real Time 5 Min	pjm_lmp_real_time_5_min	03/31/2018	06/21/2025, 10:07 AM PDT
NYISO
LMP Real Time 5 Min	nyiso_lmp_real_time_5_min	12/31/2009	06/21/2025, 10:07 AM PDT
MISO
LMP Real Time 5 Min	miso_lmp_real_time_5_min	03/24/2023	06/21/2025, 10:07 AM PDT
ISONE
LMP Real Time 5 Min	isone_lmp_real_time_5_min	01/11/2021	06/21/2025, 10:08 AM PDT
IESO
LMP Real Time 5 Min	ieso_lmp_real_time_5_min	05/01/2025	06/21/2025, 10:07 AM PDT
CAISO
LMP Real Time 5 Min	caiso_lmp_real_time_5_min	06/17/2019	06/21/2025, 10:06 AM PDT
NYISO
LMP Real Time 15 Min	nyiso_lmp_real_time_15_min	02/12/2024	06/21/2025, 08:10 AM PDT
CAISO
LMP Real Time 15 Min	caiso_lmp_real_time_15_min	09/09/2019	06/21/2025, 10:06 AM PDT
IESO
LMP Predispatch Hourly Virtual Zonal	ieso_lmp_predispatch_hourly_virtual_zonal	05/01/2025	06/21/2025, 10:07 AM PDT
IESO
LMP Predispatch Hourly Ontario Zonal	ieso_lmp_predispatch_hourly_ontario_zonal	05/01/2025	06/21/2025, 10:07 AM PDT
IESO
LMP Predispatch Hourly Intertie	ieso_lmp_predispatch_hourly_intertie	05/01/2025	06/21/2025, 10:07 AM PDT
IESO
LMP Predispatch Hourly All	ieso_lmp_predispatch_hourly_all	-	-
IESO
LMP Predispatch Hourly	ieso_lmp_predispatch_hourly	05/01/2025	06/21/2025, 10:07 AM PDT
PJM
LMP IT SCED 5 Min	pjm_lmp_it_sced_5_min	09/10/2024	06/21/2025, 10:08 AM PDT
CAISO
LMP HASP 15 Min	caiso_lmp_hasp_15_min	08/01/2019	06/21/2025, 10:02 AM PDT
IESO
LMP Day Ahead Hourly Virtual Zonal	ieso_lmp_day_ahead_hourly_virtual_zonal	05/02/2025	06/21/2025, 10:07 AM PDT
IESO
LMP Day Ahead Hourly Ontario Zonal	ieso_lmp_day_ahead_hourly_ontario_zonal	05/02/2025	06/21/2025, 10:07 AM PDT
IESO
LMP Day Ahead Hourly Intertie	ieso_lmp_day_ahead_hourly_intertie	05/02/2025	06/21/2025, 10:07 AM PDT
MISO
LMP Day Ahead Hourly Ex Post	miso_lmp_day_ahead_hourly_ex_post	01/11/2016	06/21/2025, 10:03 AM PDT
MISO
LMP Day Ahead Hourly Ex Ante	miso_lmp_day_ahead_hourly_ex_ante	12/31/2015	06/21/2025, 10:03 AM PDT
IESO
LMP Day Ahead Hourly All	ieso_lmp_day_ahead_hourly_all	-	-
SPP
LMP Day Ahead Hourly	spp_lmp_day_ahead_hourly	12/31/2014	06/21/2025, 10:08 AM PDT
PJM
LMP Day Ahead Hourly	pjm_lmp_day_ahead_hourly	12/31/2009	06/21/2025, 10:08 AM PDT
NYISO
LMP Day Ahead Hourly	nyiso_lmp_day_ahead_hourly	12/31/2016	06/21/2025, 06:35 AM PDT
MISO
LMP Day Ahead Hourly	miso_lmp_day_ahead_hourly	12/31/2020	06/21/2025, 10:07 AM PDT
ISONE
LMP Day Ahead Hourly	isone_lmp_day_ahead_hourly	12/31/2015	06/21/2025, 10:02 AM PDT
IESO
LMP Day Ahead Hourly	ieso_lmp_day_ahead_hourly	05/02/2025	06/21/2025, 10:07 AM PDT
CAISO
LMP Day Ahead Hourly	caiso_lmp_day_ahead_hourly	03/21/2019	06/20/2025, 12:17 PM PDT
ERCOT
LMP By Settlement Point	ercot_lmp_by_settlement_point	11/29/2010	06/21/2025, 10:09 AM PDT
ERCOT
LMP By Bus DAM	ercot_lmp_by_bus_dam	12/30/2017	06/20/2025, 09:27 PM PDT
ERCOT
LMP By Bus	ercot_lmp_by_bus	12/31/2019	06/21/2025, 10:06 AM PDT
IESO
Intertie Flow 5 Min	ieso_intertie_flow_5_min	05/01/2025	06/21/2025, 10:07 AM PDT
IESO
Intertie Actual Schedule Flow Hourly	ieso_intertie_actual_schedule_flow_hourly	01/31/2019	06/21/2025, 10:07 AM PDT
NYISO
Interface Limits And Flows 5 Min	nyiso_interface_limits_and_flows_5_min	11/27/2001	06/21/2025, 10:05 AM PDT
MISO
Interchange Hourly	miso_interchange_hourly	04/29/2018	06/21/2025, 10:07 AM PDT
ISONE
Interchange Hourly	isone_interchange_hourly	06/30/2017	06/21/2025, 10:08 AM PDT
MISO
Interchange 5 Min	miso_interchange_5_min	06/04/2025	06/21/2025, 10:07 AM PDT
ISONE
Interchange 15 Min	isone_interchange_15_min	06/30/2022	06/21/2025, 10:08 AM PDT
ERCOT
Indicative LMP By Settlement Point	ercot_indicative_lmp_by_settlement_point	12/31/2021	06/21/2025, 10:09 AM PDT
IESO
In Service Transmission Limits	ieso_in_service_transmission_limits	01/30/2025	06/21/2025, 10:07 AM PDT
GRIDSTATUS
ISONE Records	isone_records	12/13/2017	06/21/2025, 10:06 AM PDT
GRIDSTATUS
ISONE New Records Timeline	isone_records_timeseries	11/30/2015	06/21/2025, 10:06 AM PDT
GRIDSTATUS
IESO Records	ieso_records	01/30/2019	06/21/2025, 10:06 AM PDT
GRIDSTATUS
IESO New Records Timeline	ieso_records_timeseries	01/01/2015	06/21/2025, 10:06 AM PDT
ERCOT
Hourly Wind Report	ercot_hourly_wind_report	12/31/2017	06/21/2025, 09:56 AM PDT
SPP
Hourly Standardized Data	spp_standardized_hourly	12/31/2010	06/21/2025, 10:08 AM PDT
PJM
Hourly Standardized Data	pjm_standardized_hourly	03/31/2016	06/21/2025, 10:08 AM PDT
NYISO
Hourly Standardized Data	nyiso_standardized_hourly	12/31/2017	06/21/2025, 10:07 AM PDT
MISO
Hourly Standardized Data	miso_standardized_hourly	12/01/2022	06/21/2025, 10:07 AM PDT
ISONE
Hourly Standardized Data	isone_standardized_hourly	11/30/2015	06/21/2025, 10:06 AM PDT
IESO
Hourly Standardized Data	ieso_standardized_hourly	12/31/2014	06/21/2025, 10:08 AM PDT
ERCOT
Hourly Standardized Data	ercot_standardized_hourly	12/31/2016	06/21/2025, 10:09 AM PDT
CAISO
Hourly Standardized Data	caiso_standardized_hourly	04/10/2018	06/21/2025, 10:08 AM PDT
ERCOT
Hourly Solar Report	ercot_hourly_solar_report	06/30/2022	06/21/2025, 09:57 AM PDT
ERCOT
Hourly Resource Outage Capacity Reports	ercot_hourly_resource_outage_capacity_reports	10/21/2013	06/21/2025, 10:00 AM PDT
SPP
Hourly Load	spp_hourly_load	12/31/2010	06/20/2025, 03:00 PM PDT
ERCOT
Highest Price AS Offer Selected	ercot_highest_price_as_offer_selected	12/28/2016	06/21/2025, 01:26 AM PDT
EIA
Henry Hub Natural Gas Spot Prices Daily	eia_henry_hub_natural_gas_spot_prices_daily	12/19/1993	06/20/2025, 08:32 PM PDT
IESO
HOEP Real Time Hourly	ieso_hoep_real_time_hourly	04/30/2002	05/17/2025, 05:30 AM PDT
IESO
HOEP Historical Hourly	ieso_hoep_historical_hourly	04/30/2002	05/13/2025, 07:17 AM PDT
IESO
Generator Report Hourly	ieso_generator_report_hourly	10/19/2023	06/21/2025, 10:07 AM PDT
MISO
Generation Outages Forecast	miso_generation_outages_forecast	12/31/2021	06/20/2025, 04:50 PM PDT
MISO
Generation Outages Estimated	miso_generation_outages_estimated	12/31/2021	06/20/2025, 04:50 PM PDT
SPP
Generation Capacity On Outage	spp_generation_capacity_on_outage	10/05/2016	06/21/2025, 10:08 AM PDT
CAISO
Fuel Regions	caiso_fuel_regions	-	06/21/2025, 10:00 AM PDT
CAISO
Fuel Prices And Descriptions	caiso_fuel_prices_and_descriptions	-	-
CAISO
Fuel Prices	caiso_fuel_prices	04/01/2009	06/21/2025, 10:07 AM PDT
NYISO
Fuel Mix Raw	nyiso_fuel_mix_raw	12/31/2017	06/21/2025, 10:07 AM PDT
ERCOT
Fuel Mix Instantaneous	ercot_fuel_mix_instantaneous	04/12/2023	06/21/2025, 10:08 AM PDT
PJM
Fuel Mix Hourly	pjm_fuel_mix_hourly	12/31/2015	06/21/2025, 10:07 AM PDT
EIA
Fuel Mix Hourly	eia_fuel_mix_hourly	06/30/2018	06/21/2025, 10:01 AM PDT
SPP
Fuel Mix Detailed	spp_fuel_mix_detailed	12/31/2017	06/21/2025, 10:08 AM PDT
ERCOT
Fuel Mix Detailed	ercot_fuel_mix_detailed	02/26/2025	06/21/2025, 10:08 AM PDT
SPP
Fuel Mix	spp_fuel_mix	12/31/2010	06/21/2025, 10:08 AM PDT
PJM
Fuel Mix	pjm_fuel_mix	03/31/2016	06/21/2025, 09:15 AM PDT
NYISO
Fuel Mix	nyiso_fuel_mix	12/31/2017	06/21/2025, 10:07 AM PDT
MISO
Fuel Mix	miso_fuel_mix	12/01/2022	06/21/2025, 10:09 AM PDT
ISONE
Fuel Mix	isone_fuel_mix	11/30/2015	06/21/2025, 10:08 AM PDT
IESO
Fuel Mix	ieso_fuel_mix	12/31/2014	06/21/2025, 10:07 AM PDT
ERCOT
Fuel Mix	ercot_fuel_mix	12/31/2016	06/21/2025, 10:08 AM PDT
CAISO
Fuel Mix	caiso_fuel_mix	04/10/2018	06/21/2025, 10:08 AM PDT
IESO
Forecast Surplus Baseload Generation	ieso_forecast_surplus_baseload_generation	04/21/2023	06/21/2025, 10:07 AM PDT
ISONE
External Flows 5 Min	isone_external_flows_5_min	06/30/2022	06/21/2025, 10:08 AM PDT
ERCOT
Estimated Coincident Peak Load	ercot_estimated_coincident_peak_load	-	-
ERCOT
Energy Storage Resources	ercot_energy_storage_resources	12/05/2023	06/21/2025, 10:08 AM PDT
ERCOT
Electrical Buses	ercot_electrical_buses	-	-
GRIDSTATUS
ERCOT Records	ercot_records	03/21/2021	06/21/2025, 10:06 AM PDT
GRIDSTATUS
ERCOT New Records Timeline	ercot_records_timeseries	01/01/2017	06/21/2025, 10:06 AM PDT
PJM
Dispatched Reserves Verified	pjm_dispatched_reserves_verified	12/31/2017	06/21/2025, 10:08 AM PDT
PJM
Dispatched Reserves Prelim	pjm_dispatched_reserves_prelim	02/03/2025	06/21/2025, 10:08 AM PDT
ERCOT
Day Ahead Load Forecast	ercot_load_forecast_dam	-	-
PJM
Day Ahead Demand Bids	pjm_day_ahead_demand_bids	06/01/2000	06/21/2025, 10:08 AM PDT
ERCOT
DAM Total Energy Sold	ercot_dam_total_energy_sold	01/01/2018	06/21/2025, 10:09 AM PDT
ERCOT
DAM Total Energy Purchased	ercot_dam_total_energy_purchased	01/01/2018	06/21/2025, 10:09 AM PDT
ERCOT
DAM System Lambda	ercot_dam_system_lambda	01/01/2017	06/21/2025, 10:08 AM PDT
ERCOT
DAM PTP Obligation Option Awards 60 Day	ercot_dam_ptp_obligation_option_awards_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM PTP Obligation Option 60 Day	ercot_dam_ptp_obligation_option_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM PTP Obligation Bids 60 Day	ercot_dam_ptp_obligation_bids_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM PTP Obligation Bid Awards 60 Day	ercot_dam_ptp_obligation_bid_awards_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM Load Resource AS Offers 60 Day	ercot_dam_load_resource_as_offers_60_day	08/31/2011	06/21/2025, 08:05 AM PDT
ERCOT
DAM Load Resource 60 Day	ercot_dam_load_resource_60_day	06/29/2011	06/21/2025, 08:05 AM PDT
ERCOT
DAM Generation Resource AS Offers 60 Day	ercot_dam_gen_resource_as_offers_60_day	08/31/2011	06/21/2025, 08:05 AM PDT
ERCOT
DAM Generation Resource 60 Day	ercot_dam_gen_resource_60_day	06/29/2011	06/21/2025, 08:05 AM PDT
ERCOT
DAM Energy Only Offers 60 Day	ercot_dam_energy_only_offers_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM Energy Only Offer Awards 60 Day	ercot_dam_energy_only_offer_awards_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM Energy Bids 60 Day	ercot_dam_energy_bids_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
ERCOT
DAM Energy Bid Awards 60 Day	ercot_dam_energy_bid_awards_60_day	12/31/2012	06/21/2025, 08:05 AM PDT
CAISO
Curtailment Aggregated Hourly	caiso_curtailment_aggregated_hourly	06/30/2016	-
CAISO
Curtailment	caiso_curtailment	01/01/2017	06/21/2025, 10:07 AM PDT
CAISO
Curtailed Non Operational Generator Report	caiso_curtailed_non_operational_generator_report	06/18/2021	06/21/2025, 08:37 AM PDT
ISONE
Cleared Load Day Ahead Hourly	isone_cleared_load_day_ahead_hourly	06/30/2017	06/20/2025, 09:01 PM PDT
ERCOT
Capacity Forecast	ercot_capacity_forecast	03/27/2024	06/21/2025, 10:08 AM PDT
ERCOT
Capacity Committed	ercot_capacity_committed	03/26/2024	06/21/2025, 10:08 AM PDT
ERCOT
COP Adjustment Period Snapshot 60 Day	ercot_cop_adjustment_period_snapshot_60_day	11/30/2010	06/21/2025, 03:57 AM PDT
EIA
CO2 Emissions	eia_co2_emissions	06/30/2018	06/20/2025, 08:32 PM PDT
GRIDSTATUS
CAISO Records	caiso_records	07/21/2018	06/21/2025, 10:05 AM PDT
GRIDSTATUS
CAISO New Records Timeline	caiso_records_timeseries	04/10/2018	06/21/2025, 10:05 AM PDT
MISO
Binding Constraints Real Time 5 Min	miso_binding_constraints_real_time_5_min	12/31/2021	06/21/2025, 10:07 AM PDT
MISO
Binding Constraints Day Ahead Hourly	miso_binding_constraints_day_ahead_hourly	01/01/2022	06/20/2025, 10:00 PM PDT
MISO
Binding Constraint Overrides Real Time 5 Min	miso_binding_constraint_overrides_real_time_5_min	01/01/2022	06/21/2025, 10:07 AM PDT
NYISO
BTM Solar Forecast	nyiso_btm_solar_forecast	11/16/2020	06/21/2025, 10:07 AM PDT
NYISO
BTM Solar	nyiso_btm_solar	11/16/2020	06/21/2025, 10:07 AM PDT
ISONE
BTM Solar	isone_btm_solar	11/30/2020	06/21/2025, 10:08 AM PDT
EIA
BA Interchange Hourly	eia_ba_interchange_hourly	06/30/2015	06/21/2025, 10:01 AM PDT
ERCOT
Available Seasonal Capacity Forecast	ercot_available_seasonal_capacity_forecast	03/27/2024	06/21/2025, 10:08 AM PDT
PJM
Area Control Error	pjm_area_control_error	01/08/2025	06/21/2025, 10:08 AM PDT
GRIDSTATUS
All Records Timeseries	all_records_timeseries	12/31/2010	06/21/2025, 10:07 AM PDT
GRIDSTATUS
All Records	all_records	12/13/2017	06/21/2025, 10:07 AM PDT
IESO
Adequacy Report Forecast	ieso_adequacy_report_forecast	07/24/2024	06/21/2025, 10:06 AM PDT
ERCOT
AS Reports	ercot_as_reports	08/26/2011	06/21/2025, 01:42 AM PDT
CAISO
AS Procurement DAM	caiso_as_procurement_dam	01/01/2010	06/21/2025, 10:07 AM PDT
NYISO
AS Prices Real Time 5 Min	nyiso_as_prices_real_time_5_min	06/22/2016	06/21/2025, 10:07 AM PDT
NYISO
AS Prices Day Ahead Hourly	nyiso_as_prices_day_ahead_hourly	06/22/2016	06/21/2025, 06:45 AM PDT
SPP
AS Prices	spp_as_prices	12/31/2013	06/20/2025, 10:01 PM PDT
ERCOT
AS Prices	ercot_as_prices	11/28/2010	06/21/2025, 10:08 AM PDT
CAISO
AS Prices	caiso_as_prices	01/01/2010	06/21/2025, 10:07 AM PDT
ERCOT
AS Plan	ercot_as_plan	11/28/2010	06/21/2025, 03:00 AM PDT
PJM
AS Market Results Real Time	pjm_as_market_results_real_time	09/01/2022	06/21/2025, 10:08 AM PDT
PJM
AS Market Results DAM	pjm_as_market_results_dam	09/30/2022	06/21/2025, 10:08 AM PDT
PJM
90-Day Generation Outages Forecast	pjm_outages_90_day_forecast	12/31/2012	06/21/2025, 01:02 AM PDT
SPP
5 Minute Standardized Data	spp_standardized_5_min	12/31/2010	06/21/2025, 10:08 AM PDT
PJM
5 Minute Standardized Data	pjm_standardized_5_min	03/31/2016	06/21/2025, 10:08 AM PDT
NYISO
5 Minute Standardized Data	nyiso_standardized_5_min	12/31/2017	06/21/2025, 10:07 AM PDT
MISO
5 Minute Standardized Data	miso_standardized_5_min	12/01/2022	06/21/2025, 10:07 AM PDT
ISONE
5 Minute Standardized Data	isone_standardized_5_min	11/30/2015	06/21/2025, 10:06 AM PDT
IESO
5 Minute Standardized Data	ieso_standardized_5_min	12/31/2014	06/21/2025, 10:08 AM PDT
ERCOT
5 Minute Standardized Data	ercot_standardized_5_min	12/31/2016	06/21/2025, 10:09 AM PDT
CAISO
5 Minute Standardized Data	caiso_standardized_5_min	04/10/2018	06/21/2025, 10:08 AM PDT



## Project Plan: The Energy Arbitrage Simulator

### 1. High-Level Vision

To build an interactive platform that allows users to simulate the impact of various real-world events (like weather changes, power plant outages, or demand spikes) on the U.S. energy grid. Our system will feature a map-based visualization and a natural language chat interface. It will use AI and a wealth of historical data to forecast changes in energy prices, the generation mix, and the behavior of major energy consumers like Bitcoin miners, ultimately revealing arbitrage opportunities.

### 2. The Core Idea: "Simulate a Scenario"

This is the central user journey. We will create a simple but powerful loop for the user:

1.  **User Asks a Question:** The user types a natural language prompt into a chat box.
    *   *Example:* "What happens if a major heatwave hits Texas next week?"
    *   *Example:* "Show me the effect of a 50% drop in solar output in California."

2.  **AI Interprets the Scenario:** An LLM (like GPT) parses the user's prompt to extract the key parameters of the simulation.
    *   *Input:* "What happens if a major heatwave hits Texas next week?"
    *   *AI Output (JSON):* `{ "event": "heatwave", "location": "ERCOT", "intensity": "high" }`

3.  **Find a Historical Analog (RAG):** Instead of building a complex predictive model from scratch, we find a real historical precedent in our data that matches the scenario. This is a Retrieval-Augmented Generation (RAG) approach.
    *   For a "high heatwave in ERCOT," the system will search our datasets for past periods where temperatures in Texas were unusually high.
    *   It will then retrieve all associated data for that period: energy prices (LMP), energy demand (load), solar/wind output, the fuel mix, etc.

4.  **Simulate & Visualize:** The historical data becomes the basis for our simulation.
    *   **The Map:** We'll display a map of the relevant energy grid (e.g., Texas). The map will be color-coded to show the simulated energy prices across different zones.
    *   **The Charts:** We'll show time-series graphs of the key metrics from the historical analog: Price ($/MWh), Demand (GW), and the Generation Mix (Solar, Wind, Gas, etc.).
    *   **The Narrative:** A second LLM call will synthesize the data into a human-readable story. "Based on a similar heatwave in July 2022, we can expect energy prices to spike to over $200/MWh in the late afternoon as demand outstrips solar production..."

### 3. Step-by-Step Hackathon Implementation Plan

This is a practical, phased approach to ensure you have a working, impressive demo.

#### Phase 1: The Data Foundation & Backend (The First 12 Hours)

1.  **Pick Your Battles (Data Selection):**
    *   **Focus on ONE Independent System Operator (ISO) first.** **ERCOT (Texas)** is the perfect starting point. You have the richest data for it, including the crucial `ercot_temperature_forecast_by_weather_zone` which is essential for your weather-based scenarios.
    *   **Select Key Datasets.** Don't try to use all 600+. Start with the essentials:
        *   **Prices:** `ercot_spp_day_ahead_hourly` (The price of electricity at different points on the grid)
        *   **Demand:** `ercot_load_forecast_by_weather_zone` (How much power is needed)
        *   **Renewables:** `ercot_solar_actual_and_forecast_hourly`, `ercot_wind_actual_and_forecast_hourly`
        *   **Inputs:** `ercot_temperature_forecast_by_weather_zone` (The trigger for your first scenario)
        *   **Mix:** `ercot_fuel_mix` (To show where the power is coming from)
    *   **Data Setup:** For the hackathon, download these as CSVs. Use a Python backend (FastAPI or Flask) with Pandas to load and query them. This is fast and simple.

2.  **Build the "Analog Engine" API:**
    *   Create a backend endpoint, e.g., `POST /simulate`.
    *   This endpoint receives the JSON from the AI Interpreter (e.g., `{ "event": "heatwave", ... }`).
    *   The core logic will:
        1.  Translate the event into a data query (e.g., "heatwave" -> `temperature > 100`).
        2.  Search the temperature data for a historical period matching the query.
        3.  Select the best historical match.
        4.  Retrieve all other key datasets from that same time period.
        5.  Return the collected historical data as a single JSON response.

#### Phase 2: The Frontend & AI Glue (The Next 12 Hours)

3.  **Build the User Interface:**
    *   Use a simple web framework (React, Svelte, or even vanilla HTML/JS with a library like Bootstrap).
    *   Create a simple layout: a chat input on one side, and a placeholder for a map and charts on the other.

4.  **Wire up the AI Interpreter:**
    *   When the user submits a query, your frontend calls your backend.
    *   The backend makes an API call to an LLM (e.g., OpenAI) with a carefully engineered prompt to transform the user's text into the structured JSON your `/simulate` endpoint needs. This is the "magic" that makes the chat interface work.

5.  **Visualize the Simulation:**
    *   When the frontend receives the data from the `/simulate` endpoint, use libraries to display it.
    *   **Map:** Use a library like [Leaflet.js](https://leafletjs.com/) to show a map of Texas. You'll need a GeoJSON file for the ERCOT weather zones, which can be found online. Color the zones based on the LMP data.
    *   **Charts:** Use [Chart.js](https://www.chartjs.org/) to create line graphs for price, demand, and generation over time.
    *   **Narrative:** Make one final LLM call, feeding it the simulation data and asking it to "explain what is happening in this scenario to a non-expert." Display this text above the charts.

#### Phase 3: The "Arbitrage" Extension (Bonus - If you have time)

6.  **Simulate Bitcoin Miner Behavior:**
    *   This is the "arbitrage" part of the prompt and will really impress the judges.
    *   Add a simple rule to your simulation logic: If the simulated energy price (LMP) exceeds a certain threshold (e.g., $60/MWh), assume that Bitcoin miners will curtail (shut down) their operations.
    *   Model this as a reduction in the `load` data.
    *   In the UI, you can add a toggle: "Simulate with Bitcoin Demand Response." When toggled, it shows a second, lower demand curve on the chart, demonstrating how flexible demand can help stabilize the grid. This directly addresses the core theme of the hackathon.

### 4. Why This Approach Is The Best Way to Win

*   **Achievable:** It cleverly sidesteps the need for complex ML model training, which is impossible in a hackathon. The RAG/Historical Analog approach is robust and quick to implement.
*   **Visually Stunning:** An interactive map and chat interface is a classic recipe for a memorable demo.
*   **AI-Powered:** It uses LLMs for what they are best at (natural language understanding and summarization) without asking them to invent data.
*   **Directly Addresses the Prompt:** It combines energy markets, AI, and even Bitcoin mining in a single, coherent application.