#PLL SSTC#
##Overview#
The PLL SSTC stands for Phase Locked Loop Solid State Tesla coil. This device produce high voltage sparks that resemble lighting by exciting a secondary coil at its resonant frequency. 
This system tracks the resonant frequency using a Phase Locked Loop(PLL) ic: CD4046. It uses the output from the PLL to drive a full bridge switching circuit at around 300-325vdc. 
It also has the capability to play audio through both Amplitute Modulation (AM) and Frequency Modulation (FM). It operates at 250khz and should switch power in the Kilowatt range. 

> ⚠️ High Voltage Warning  
> This project involves potentially lethal voltages and high-frequency/high-power switching. Do not build or operate it unless you understand the relevant electrical safety risks

##Gate Driver##
I'm using a TC4428 paired with 2 N-channel P-channel dual MOSFET IC's to produce an amplified signal capable of producing higher driving currents. Any mosfet driving ic with one inverting and one non inverting ic should work in the PCB such as the UCC27425.

##GDT##
The Gate Drive Transformer must be large enough to not saturate from driving currents and be of the correct material to work properly under such high frequencies.

##Mosfets##
My circuit shows IRFP460s as the full bridge switches but they are a bit outdated and inefficient. Much better alternatives exist, IGBT's can also be used instead

##Primary##
Make sure the primary impedance is high enough such that your switches can handle the currents. 
