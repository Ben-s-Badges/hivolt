# Module to deal with the screen
#
# 
from machine import Pin, SPI, PWM, mem32
from micropython import const
import rp2

class screenDriver:
    # Screen GPIOs
    GLOBAL_nCLR = Pin(5, mode=Pin.OUT, value=0)
    COL_CLK = Pin(6, mode=Pin.OUT, value=0)
    COL_DATA = Pin(7, mode=Pin.OUT, value=0)
    COL_nOE = Pin(9, mode=Pin.OUT, value=1)
    RCLK = Pin(8, mode=Pin.OUT, value=0)

    LEFT_PWM1   = PWM(Pin(16), freq=100000, duty_u16=0)
    LEFT_PWM2   = PWM(Pin(17), freq=100000, duty_u16=0)
    RIGHT_PWM1  = PWM(Pin(18), freq=100000, duty_u16=0)
    RIGHT_PWM2  = PWM(Pin(19), freq=100000, duty_u16=0)
    BOTTOM_PWM1 = PWM(Pin(20), freq=100000, duty_u16=0)
    BOTTOM_PWM2 = PWM(Pin(21), freq=100000, duty_u16=0)
    BOLT_PWM    = PWM(Pin(28), freq=100000, duty_u16=0)

    # Screen: 240 columns x 8 rows
    # Bolt: 8 columns x 8 rows
    RAW_SCREEN_SIZE = const(280)

    # Raw screen (after mangling) is triple buffered and refreshed by PIO
    _rawscreen = [ bytearray([0xff] * RAW_SCREEN_SIZE), bytearray([0xff] * RAW_SCREEN_SIZE), bytearray([0xff] * RAW_SCREEN_SIZE) ]
    _rawscreen_refreshfrom = 0
    
    # Buffer of next bolt update
    _boltBuffer = bytearray(8)

    # Bolt offsets in raw buffer, then every 56 after
    # So 3, 59, 115, 171, 227. For full brightness all must be written with the same data
    _boltoffsets = [3,4,13,22,31,32,41,50]
    
    # Count of refreshes
    _refreshcounter = 0

    # GPIO2 = ROW_CLK		# sideset base
    # GPIO3 = ROW_DATA		# out base
    # GPIO5 = GLOBAL_nCLR
    # GPIO6 = COL_CLK		# set base
    # GPIO7 = COL_DATA
    # GPIO8 = RCLK

    @rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW),
                 sideset_init=(rp2.PIO.OUT_LOW),
                 set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
                 autopull=True, fifo_join=rp2.PIO.JOIN_NONE, out_shiftdir=rp2.PIO.SHIFT_LEFT)
    def clearpiofifo():
        pGLOBAL_nCLR = 1
        pRCLK = 8        
        wrap_target()
        set(pins, 0)					# At startup, we clear the shift register
        set(pins, pGLOBAL_nCLR)
        set(pins, pGLOBAL_nCLR + pRCLK)
        wrap()

    @rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW),
                 sideset_init=(rp2.PIO.OUT_LOW),
                 set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
                 autopull=True, fifo_join=rp2.PIO.JOIN_TX, out_shiftdir=rp2.PIO.SHIFT_LEFT)
    def refresh():
        pGLOBAL_nCLR = 1
        pCOL_CLK = 2
        pCOL_DATA = 4
        pRCLK = 8
        set(pins, 0)					# At startup, we clear the shift register
        set(pins, pGLOBAL_nCLR)

        wrap_target()
        set(x, 18)						# 40 columns, 2 per loop

        label('colloop')
        
        set(y, 27)						# Clock out 56 bits, 2 at a time
        label('rowloop1')
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        nop().side(1)					# Set ROW_CLK high
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        jmp(y_dec, 'rowloop1').side(1) 	# Set ROW_CLK high

        set(pins, pGLOBAL_nCLR + pRCLK)
        set(pins, pGLOBAL_nCLR + pCOL_CLK)
        
        set(y, 27)						# Clock out 56 bits, 2 at a time
        label('rowloop2')
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        nop().side(1)					# Set ROW_CLK high
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        jmp(y_dec, 'rowloop2').side(1) 	# Set ROW_CLK high
        
        set(pins, pGLOBAL_nCLR + pRCLK)
        set(pins, pGLOBAL_nCLR + pCOL_CLK)
        
        jmp(x_dec, 'colloop')
        
        # Last column has to clock column in high
        set(y, 27)						# Clock out 56 bits, 2 at a time
        label('rowloop3')
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        nop().side(1)					# Set ROW_CLK high
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        jmp(y_dec, 'rowloop3').side(1) 	# Set ROW_CLK high

        set(pins, pGLOBAL_nCLR + pRCLK)
        set(pins, pGLOBAL_nCLR + pCOL_CLK)

        set(y, 27)						# Clock out 56 bits, 2 at a time
        label('rowloop4')
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        nop().side(1)					# Set ROW_CLK high
        out(pins, 1).side(0)			# Clock ROW_DATA out & ROW_CLK low
        jmp(y_dec, 'rowloop4').side(1) 	# Set ROW_CLK high

        set(pins, pGLOBAL_nCLR + pCOL_DATA + pRCLK)
        set(pins, pGLOBAL_nCLR + pCOL_DATA + pCOL_CLK)

        wrap()

    # Interrupt handler for DMA; just reset the read pointer so we use the same data over and over
    def dmairq(self, dma):
        # Re-initialize this channel for when it comes round again
        dma.read = self._rawscreen[self._rawscreen_refreshfrom]
        dma.count = RAW_SCREEN_SIZE//4
        
        # Increment refresh count
        self._refreshcounter += 1

    def dmaabort(self):
        # Sometimes, on warm boot, DMA channels are all showing busy in their control register
        # To fix this, we just abort all the channels in the DMA_ABORT register before we get going
        # This seems to work, even though DMA_ABORT reads zero in these cases. Freaky.
        DMA_ABORT = const(0x50000444)
        mem32[DMA_ABORT] = (1 << self._dma0.channel) | (1 << self._dma1.channel) | (1 << self._dma2.channel)
        
    # Start refreshing
    def startRefresh(self):
        # Clear up any old stuff
        self.dmaabort()

        # ...and a PIO state machine for refresh
        self._sm = rp2.StateMachine(0, self.refresh, freq=750_000, set_base=Pin(5), sideset_base=Pin(2), out_base=Pin(3))
        
        # Transfer words, don't increment write address, chain to dma1, irq
        c = self._dma0.pack_ctrl(inc_write=False, treq_sel=0, irq_quiet=False, chain_to=self._dma1.channel)
        self._dma0.config(read=self._rawscreen[0], write=self._sm, count=RAW_SCREEN_SIZE//4, ctrl=c)
        self._dma0.irq(handler=self.dmairq)

        # Transfer words, don't increment write address, chain to dma2, irq
        c = self._dma1.pack_ctrl(inc_write=False, treq_sel=0, irq_quiet=False, chain_to=self._dma2.channel)
        self._dma1.config(read=self._rawscreen[1], write=self._sm, count=RAW_SCREEN_SIZE//4, ctrl=c)
        self._dma1.irq(handler=self.dmairq)
        
        # Transfer words, don't increment write address, chain to dma0, irq
        c = self._dma2.pack_ctrl(inc_write=False, treq_sel=0, irq_quiet=False, chain_to=self._dma0.channel)
        self._dma2.config(read=self._rawscreen[2], write=self._sm, count=RAW_SCREEN_SIZE//4, ctrl=c)
        self._dma2.irq(handler=self.dmairq)
        
        # Start PIO engine, enable first DMA channel
        self._dma0.active(1)
        self._sm.active(1)
        self.COL_nOE.off()        
        
    # Stop refreshing
    def stopRefresh(self):
        # Stop PIO engine & blank screen
        self._sm.active(0)
        self._dma0.active(0)
        self._dma1.active(0)
        self._dma2.active(0)
        
        # Abort DMAs
        self.dmaabort()
                
        self.COL_nOE.on()
     
    # Translate a sane format frame buffer into the one required for hardware refresh
    # Essentially, every 8 columns are swapped
    @micropython.viper
    def flushScreenViper(self, screen, destination):
        # Use ptr8() for speed
        sp = ptr8(screen)
        rp = ptr8(self._rawscreen[destination])
        
        # Note that this is very much unoptimized, but it's late and it works
        for x in range(0, 240):
            col_in_block = 8 - (x&7)
            block_in_section = (x >> 3) % 5
            section = (x // 40) + 1
            address = (block_in_section*56)+(col_in_block*7)-section
            address = (address & 0xffc) | (3-(address&3))
            rp[address] = sp[x] ^ 0xff       
    
    def flushScreen(self, screen):
        # Load new data into idle screen buffer, ie the next one
        destination = (self._rawscreen_refreshfrom + 1) % 3
        self.flushScreenViper(screen, destination)
        for i in range(0, 8):
            for j in range(0, 5):
                self._rawscreen[destination][(j*56) + self._boltoffsets[i]] = self._boltBuffer[i]
        
        # Use this new raw screen for the next refresh
        self._rawscreen_refreshfrom = destination

    @micropython.native
    def flushBolt(self, bolt):
        # Just copy bolt data locally, we will flush it at the next flushScreen
        for i in range(0, 8):
            self._boltBuffer[i] = bolt[i] ^ 0xff

    # How many refreshes we've completed
    def refreshes(self):
        r = self._refreshcounter
        self._refreshcounter = 0        
        return r
    
    def __init__(self):
        # Ensure shift registers are clear
        self.GLOBAL_nCLR.off()
        self.RCLK.on()
        self.RCLK.off()
        self.GLOBAL_nCLR.on()

        # Get three DMA engines
        self._dma0 = rp2.DMA()
        self._dma1 = rp2.DMA()
        self._dma2 = rp2.DMA()
        
        # After many attempts, it turns out the best way to ensure PIO and DMA are happy is...
        # ...to turn it off and on again
        self.startRefresh()
        self.stopRefresh()
