# PLL SSTC

## Overview
The PLL SSTC stands for Phase Locked Loop Solid State Tesla coil. This device produces high voltage sparks that resemble lightning by exciting a secondary coil at its resonant frequency.

This system tracks the resonant frequency using a Phase Locked Loop (PLL) IC: CD4046. It uses the output from the PLL to drive a full bridge switching circuit at around 300-325VDC.

It also has the capability to play audio through both Amplitude Modulation (AM) and Frequency Modulation (FM). It operates at 250kHz and should switch power in the Kilowatt range.
<img width="3508" height="2480" alt="image" src="https://github.com/user-attachments/assets/0178ad6c-eae1-4e15-935a-720e6caf29e8" />

<img width="881" height="893" alt="image" src="https://github.com/user-attachments/assets/f0245a84-77a2-4823-8ec7-9ad1d2083f6c" />

> ⚠️ High Voltage Warning  
> This project involves potentially lethal voltages and high-frequency/high-power switching. Do not build or operate it unless you understand the relevant electrical safety risks.

## Gate Driver
I'm using a TC4428 paired with 2 N-channel/P-channel dual MOSFET ICs to produce an amplified signal capable of producing higher driving currents. Any MOSFET driving IC with one inverting and one non-inverting output should work in the PCB, such as the UCC27425.

## GDT
The Gate Drive Transformer must be large enough to not saturate from driving currents and be of the correct material to work properly under such high frequencies.

## Mosfets
My circuit shows IRFP460s as the full bridge switches, but they are a bit outdated and inefficient. Much better alternatives exist — IGBTs can also be used instead.

## Primary
Make sure the primary impedance is high enough such that your switches can handle the currents.
