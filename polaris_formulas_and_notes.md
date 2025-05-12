**Pump rate**, [Bucher_pump_specs](https://arisswitzerland.sharepoint.com/:w:/r/_layouts/15/Doc.aspx?sourcedoc=%7B5A481993-C3AF-4969-A083-93957ABD08AC%7D&file=Bucher%20CU%20Cooperation.docx&action=default&mobileredirect=true)

`max_pump_rate_physical`$=(0.32 cm^3/rev) * (4280 rev/min) / (60 s/min) = 22.8266666667 cm^3/s = 0.02283 L/s = 0.00002283 m^3/s$

**Mass**, [general_system_criteria_sharepoint](https://arisswitzerland.sharepoint.com/:x:/r/_layouts/15/Doc.aspx?sourcedoc=%7B7C5465AD-30C2-4B8E-A9CC-A569785C1106%7D&file=general%20system%20criteria.xlsx&action=default&mobileredirect=true)

**Volumes and lengths**, [onshape](https://arisspace.onshape.com/documents/4414650879a95fc79e06ee1e/w/aa45838af7379fe155e4e22d/e/dffd0c078743992dc8e4b370)

- `tank_volume` = $0.002275m^3$
- `length`=$1.0$
- `radius`=$0.14$

**Water density**, [Greifensee](https://www.datalakes-eawag.ch/datadetail/1063)
- `density`=$999 kg / m^3$

NOTE:
- `max_pump_rate`=`max_pump_rate_physical`/`tank_volume`

IDEAS:
- Optimisation algorithm for PIDs: loss function proportional to `time` and accuracy in reaching desired `low_depth` and `high_depth`