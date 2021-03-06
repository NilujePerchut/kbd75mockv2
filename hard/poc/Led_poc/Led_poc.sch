EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Switch:SW_Push SW1
U 1 1 6097FE19
P 5000 2400
F 0 "SW1" V 4954 2548 50  0000 L CNN
F 1 "SW_Push" V 5045 2548 50  0000 L CNN
F 2 "Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB" H 5000 2600 50  0001 C CNN
F 3 "~" H 5000 2600 50  0001 C CNN
	1    5000 2400
	0    1    1    0   
$EndComp
$Comp
L LED:WS2812B D1
U 1 1 60980DEA
P 5000 3200
F 0 "D1" H 5344 3246 50  0000 L CNN
F 1 "WS2812B" H 5344 3155 50  0000 L CNN
F 2 "Led_poc:SK6812" H 5050 2900 50  0001 L TNN
F 3 "https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf" H 5100 2825 50  0001 L TNN
	1    5000 3200
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW2
U 1 1 6098287A
P 6450 2400
F 0 "SW2" V 6404 2548 50  0000 L CNN
F 1 "SW_Push" V 6495 2548 50  0000 L CNN
F 2 "Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB" H 6450 2600 50  0001 C CNN
F 3 "~" H 6450 2600 50  0001 C CNN
	1    6450 2400
	0    1    1    0   
$EndComp
$Comp
L LED:WS2812B D2
U 1 1 60982B8A
P 6450 3200
F 0 "D2" H 6794 3246 50  0000 L CNN
F 1 "WS2812B" H 6794 3155 50  0000 L CNN
F 2 "Led_poc:SK6812" H 6500 2900 50  0001 L TNN
F 3 "https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf" H 6550 2825 50  0001 L TNN
	1    6450 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	5300 3200 6150 3200
Wire Wire Line
	5000 2900 6450 2900
Wire Wire Line
	5000 3500 6450 3500
Wire Wire Line
	5000 2600 6450 2600
Wire Wire Line
	6450 2000 6450 2200
$Comp
L Connector_Generic:Conn_01x06 J1
U 1 1 609866A4
P 3500 2300
F 0 "J1" H 3418 1775 50  0000 C CNN
F 1 "Conn_01x06" H 3418 1866 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical" H 3500 2300 50  0001 C CNN
F 3 "~" H 3500 2300 50  0001 C CNN
	1    3500 2300
	-1   0    0    1   
$EndComp
Wire Wire Line
	3700 2000 6450 2000
Wire Wire Line
	3700 2100 5000 2100
Wire Wire Line
	5000 2100 5000 2200
Wire Wire Line
	3700 2200 4850 2200
Wire Wire Line
	4850 2200 4850 2600
Wire Wire Line
	4850 2600 5000 2600
Connection ~ 5000 2600
Wire Wire Line
	3700 2400 4650 2400
Wire Wire Line
	4650 2400 4650 3200
Wire Wire Line
	4650 3200 4700 3200
NoConn ~ 6750 3200
$Comp
L Device:C C1
U 1 1 6098EB27
P 7350 3200
F 0 "C1" H 7465 3246 50  0000 L CNN
F 1 "100nF" H 7465 3155 50  0000 L CNN
F 2 "Capacitor_SMD:C_0201_0603Metric_Pad0.64x0.40mm_HandSolder" H 7388 3050 50  0001 C CNN
F 3 "~" H 7350 3200 50  0001 C CNN
	1    7350 3200
	1    0    0    -1  
$EndComp
$Comp
L Device:C C2
U 1 1 6098EFC5
P 7850 3200
F 0 "C2" H 7965 3246 50  0000 L CNN
F 1 "100nF" H 7965 3155 50  0000 L CNN
F 2 "Capacitor_SMD:C_0201_0603Metric_Pad0.64x0.40mm_HandSolder" H 7888 3050 50  0001 C CNN
F 3 "~" H 7850 3200 50  0001 C CNN
	1    7850 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	6450 2900 7350 2900
Connection ~ 6450 2900
Connection ~ 6450 3500
Wire Wire Line
	7350 3350 7350 3500
Wire Wire Line
	6450 3500 7350 3500
Wire Wire Line
	7350 3050 7350 2900
Wire Wire Line
	7350 2900 7850 2900
Wire Wire Line
	7850 2900 7850 3050
Connection ~ 7350 2900
Wire Wire Line
	7350 3500 7850 3500
Wire Wire Line
	7850 3500 7850 3350
Connection ~ 7350 3500
Text Label 5700 2900 0    50   ~ 0
VDD
Text Label 5700 3500 0    50   ~ 0
GND
Wire Wire Line
	4150 2300 3700 2300
Wire Wire Line
	4150 2500 3700 2500
Text Label 4000 2500 0    50   ~ 0
VDD
Text Label 4000 2300 0    50   ~ 0
GND
$EndSCHEMATC
