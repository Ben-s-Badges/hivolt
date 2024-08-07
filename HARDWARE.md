# hivolt
Software and hardware details for the Ben's Badges HiVolt badge 2024

# Hardware

Here's a walk-through of the hardware.

## Power

Power comes from an 1,100mAh LiPoly cell which connects via a standard JST 2 pin connector. This cell has UL approvals and includes a PCM for over charge and over discharge and over current protection.

Reverse voltage protection - some batteries have a different polarity - is provided by Q3, which introduces little to no voltage drop. The battery is charged at a maximum of 256mA using a TP4054 linear charger, with a 4.2v float voltage. The battery will charge whether or not the badge is turned on. Charge power comes from the USB-C connector, which includes 5k1 resistors to request 5v from a compatible USB-PD source.

All the active circuitry runs from 3.3v, which is supplied by a Zetta ZD8028 buck regulator (~90% efficient). The enable pin on this regulator is connected to the slide power switch. When powered off, the badge consumes a handful of microamps.

Battery voltage is fed via a 100k/33k divider into the VOLT_SENSE (GPIO28/ADC0) input, gated by VOLT_EN (GPIO4). To read the battery voltage, drive VOLT_EN high and wait a few milliseconds for C51 to charge, take the sample, then lower VOLT_EN. This enable/disable prevents power leakage through the sense network, as this is upstream of the power switch.

The VBUS voltage can also be read by the MCU via a 150k/100k divider that feeds into VBUS_SENSE (GPIO29/ADC1). There is no gate on this as it's minimal extra draw on USB.

## MCU

The MCU used is the RP2040, with a 2MB (16Mbit) WinBond QSPI for storage. The board has both RESET and BOOT switches, with a small hole in the housing to access the BOOT one - if you want to put the RP2040 in DFU mode, turn the badge off, hold the BOOT switch with a paperclip, and then turn the badge on.

The MCU wiring is much the same as the RP2040 reference design. USB is connected to the USB-C connector, allowing easy firmware updates.

## Accelerometer

An ST LIS2DH12TR accelerometer is on board, connected to the RP2040 I2C via SDA (GPIO12) and SCL (GPIO13). ACCEL_INT on GPIO14 allows the MCU to get interrupts from the part. You should turn the RP2040 pull-up on for this pin as there is no external pull-up resitor.

## Microphone

An analog MEMS top port microphone (ZTS6117H) provides audio input. It is AC coupled to an LM321 to amplify the signal, and fed into MIC_OUT (GPIO29/ADC3). The mic and LM321 are powered from MIC_SUPPLY (GPIO11) so this needs to be driven high to enable audio input. It takes about 1mA when enabled.

## Joystick

A small 5 way (4 directions + push) joystick is on the back of the badge. When moved, the joystick connects appropriate pins to ground, so you must enable pull-up resistors on the pins to read states. The corresponding GPIOs, looking at the badge with the display away from you, are: SW_LEFT (GPIO22), SW_RIGHT (GPIO23), SW_UP (GPIO24), SW_DOWN (GPIO25) and SW_PUSH (GPIO15).

## Finally, the LEDs

Here's where it gets interesting! The badge was designed to be as cheap as possible, given the number of LEDs, so I took some.... liberties with electrical specs.

Essentially, the LEDs are all driven by two shift register chains.

The column chain drives 240 columns of 8 pixels, plus 8 more columns of 8 pixels for the lightning bolt. In a refresh cycle, 1 column in 40 is driven high at a time, and the appropriate row lines are driven low, causing current to flow and the LED to light. Moving to the next column just involves providing a single rising edge on the column clock then another on RCLK, so requires no hardware assist.

The "bolt" LEDs are at the end of this chain, and because there are only 8 columns (vs 40), the shift-out of this last shift register is ORed with the input using a 74LVC1G32 (U47), meaning a 1 that comes into the column chain from the display end will get recycled, causing the bolt to refresh at 5x the rate (40/8) of the other pixels. This is why it's brighter.

This also means each column output of a shift register is supplying current to up to 8 LEDs, which does lead to a slight dimming the more pixels that are driven as it's a standard 595D part. In theory, because each set of 40 columns has a PWM'ed OE signal, the brightness could be leveled so that any number of pixels lit would be at the same intensity. This is left as an exercise to the reader :)

The refresh task looks like this:

### Setup

- Deassert COL_nOE (GPIO9 high)
- Assert then release GLOBAL_CLR (GPIO5 low then high again)
- Set column counter to zero

### Loop

- If column counter is zero, set COL_DATA (GPIO7) high, otherwise set it low - this provides the '1' that walks along the columns
- Drive COL_CLK (GPIO6) high then low, to clock in the COL_DATA
- Use SPI to send 7 bytes of row data, starting with a byte for the bolt then 6 bytes, one for each 40 column segment
- All data is now clocked in and ready to be displayed. Move it to the output register by driving RCLK (GPIO8) high then low
- Increment column counter, if it's not 40 then run loop again

Here, this is done by PIO and DMA; each screen buffer is a single DMA request. There are 3 raw buffers, all chained, and when we get a completion interrupt we reset the just-completed DMA
to point at the most recently updated buffer. There are 3 buffers because I hear that some RP2040's will issue the DMA complete IRQ before the DMA is totally complete, so this is an insurance
policy against showing an incomplete update.

The PIO/DMA thing is very nice, but look at flushScreenViper() in screen.py to see what it did to the memory layout. Some of this was self inflicted (the shift register outputs should really
be reversed) but hey, it works and I wasn't going to re-layout the PCB.

