This project aims to generate virtual traffic flow data of a 3*3 road net to visualize one day's traffic flow distribution of the intersections.

This file illustrates the process：

STEP 1: modify the value of 'Factor' of "od.mat.xml", which is a global scaling factor for the number of vehicles for each cell;

**modify_factor(factor)** 

STEP 2: generate 'od.trips.xml' by the use of 'od.mat.xml' and 'taz.net.xml', and then get the e1Detectors' result 'od.out.xml' and trip information
'tripinfo.out.xml' by 'SUMO od.sumocfg'. Just call the function 'generate_xml()'.

**generate_xml()**

STEP 3: get each edge's total flow of all time periods(set by 'det.add.xml', here is 5 min) by reading the 'od.out.xml'.

**flow_dict, time_line = get_flow_from_xml(file_path)**

STEP 4: plot the flow distribution curve of each intersection. The figures will be saved to directory 'curves1/' or 'curves2/'

**plot_flow_all_edges(flow_dict, time_line, save_dir, interval)**

Something need to be noticed:
1. The function 'generate_timeline()' is served to generate the vehicles' generating weights of different hours in one day, which has 24 points 
corresponding to the 24 hours.
2. The 'tripinfo.out.xml' is not utilized here.
3. 'net1' and 'net2' correspond to different Traffic light timing scheme, which can be seen in 'tls.xml' of each directory for details. 
So do 'curves1' and 'curves2'.