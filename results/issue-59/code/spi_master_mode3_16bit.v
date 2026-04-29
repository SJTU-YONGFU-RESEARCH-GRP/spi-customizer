module spi_master #(
    parameter MODE = 3,              // SPI Mode (0-3)
    parameter DATA_WIDTH = 16,       // Data width in bits
    parameter NUM_SLAVES = 8,        // Number of slave devices
    parameter SELECTED_SLAVE = 3,             // Selected slave index for deterministic one-hot SS
    parameter SLAVE_ACTIVE_LOW = 1,  // Slave select active level
    parameter MSB_FIRST = 1,          // Data transmission order
    parameter FIFO_DEPTH = 32,        // FIFO buffer depth
    parameter CLOCK_DIVIDER = 4,  // System clock divider
    parameter DEFAULT_DATA_ENABLED = 0,
    parameter DEFAULT_DATA_PATTERN = "a5a5",
    parameter DEFAULT_DATA_VALUE = 16'hA5A5
)(
    input  wire                  clk,        // System clock
    input  wire                  rst_n,      // Active low reset

    // Control interface
    input  wire                  start_tx,   // Start transmission
    input  wire                  start_rx,   // Start reception
    input  wire [DATA_WIDTH-1:0] tx_data,    // Data to transmit
    output reg  [DATA_WIDTH-1:0] rx_data,    // Received data
    output reg                   busy,       // Busy signal

    // SPI interface
    output reg                   sclk,       // SPI clock
    output reg                   mosi,       // Master out, slave in
    input  wire                  miso,       // Master in, slave out
    output reg [NUM_SLAVES-1:0]  ss_n,       // Slave select (active low)

    // Interrupt (optional)
    output reg                   irq         // Interrupt request
);

    // Local parameters
    localparam SCLK_HALF_PERIOD = CLOCK_DIVIDER; // Configurable SCLK period based on system clock

    // State machine states
    localparam IDLE = 3'd0;
    localparam SETUP = 3'd1;
    localparam TRANSMIT = 3'd2;
    localparam RECEIVE = 3'd3;
    localparam COMPLETE = 3'd4;

    // Registers
    reg [2:0]  state;
    reg [2:0]  next_state;
    reg [15:0] clk_counter;    // SCLK generation counter
    reg [15:0] bit_counter;    // Bit transmission counter (supports wider DATA_WIDTH values)
    reg [DATA_WIDTH-1:0] tx_shift_reg;
    reg [DATA_WIDTH-1:0] rx_shift_reg;
    reg        sclk_gen;       // SCLK generator
    reg        last_sclk;      // Previous SCLK value for edge detection

    // Clock polarity and phase for different modes
    wire CPOL = (MODE == 2) || (MODE == 3);  // Clock polarity
    wire CPHA = (MODE == 1) || (MODE == 3);  // Clock phase

    // Slave select active level
    wire SS_ACTIVE = SLAVE_ACTIVE_LOW ? 1'b0 : 1'b1;
    localparam integer SELECTED_SLAVE_CLAMP = (SELECTED_SLAVE >= 0 && SELECTED_SLAVE < NUM_SLAVES) ? SELECTED_SLAVE : 0;

    // Default data generation
    reg [DATA_WIDTH-1:0] default_data;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            default_data <= 16'hA5A5;
        end else if (DEFAULT_DATA_ENABLED) begin
            case (DEFAULT_DATA_PATTERN)
                "a5a5": default_data <= 16'hA5A5;
                "ffff": default_data <= 16'hFFFF;
                "0000": default_data <= 16'h0000;
                "5555": default_data <= 16'h5555;
                default: default_data <= 16'hA5A5;
            endcase
        end
    end

    // State machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            clk_counter <= 0;
            bit_counter <= 0;
            tx_shift_reg <= 0;
            rx_shift_reg <= 0;
            sclk <= CPOL;  // Set initial SCLK state based on CPOL
            mosi <= 0;
            ss_n <= {NUM_SLAVES{~SS_ACTIVE}};
            busy <= 0;
            irq <= 0;
            last_sclk <= CPOL;
            sclk_gen <= CPOL;
        end else begin
            state <= next_state;
            last_sclk <= sclk_gen;

            // State-specific register updates
            case (state)
                IDLE: begin
                    // Clear interrupt when acknowledged (optional)
                    if (irq) begin
                        irq <= 0;
                    end
                end

                SETUP: begin
                    // Initialize transmission
                    bit_counter <= 0;
                    tx_shift_reg <= DEFAULT_DATA_ENABLED ? default_data : tx_data;
                    rx_shift_reg <= 0;
                    // For CPHA=0, present first data bit before the first sampling edge.
                    if (!CPHA) begin
                        if (MSB_FIRST) begin
                            mosi <= DEFAULT_DATA_ENABLED ? default_data[DATA_WIDTH-1] : tx_data[DATA_WIDTH-1];
                        end else begin
                            mosi <= DEFAULT_DATA_ENABLED ? default_data[0] : tx_data[0];
                        end
                    end
                end

                COMPLETE: begin
                    // Capture received data
                    rx_data <= rx_shift_reg;
                end
            endcase

            // SCLK generation (runs during active transmission/reception)
            if (state == TRANSMIT || state == RECEIVE) begin
                if (clk_counter >= SCLK_HALF_PERIOD - 1) begin
                    clk_counter <= 0;
                    sclk_gen <= ~sclk_gen;
                end else begin
                    clk_counter <= clk_counter + 1;
                end
            end else begin
                clk_counter <= 0;
                sclk_gen <= CPOL;
            end

            // Data transmission and reception (runs during TRANSMIT/RECEIVE)
            if (state == TRANSMIT || state == RECEIVE) begin
                // SPI Mode-specific data handling
                if (CPHA == 0) begin
                    // Mode 0/2: sample on leading edge, change data on trailing edge.
                    if (sclk_gen != last_sclk) begin
                        if (sclk_gen == ~CPOL) begin
                            // Leading edge - sample data
                            if (bit_counter < DATA_WIDTH) begin
                                if (MSB_FIRST) begin
                                    if (DATA_WIDTH > 1) begin
                                        rx_shift_reg <= {rx_shift_reg[DATA_WIDTH-2:0], miso};
                                    end else begin
                                        rx_shift_reg <= miso;
                                    end
                                end else begin
                                    if (DATA_WIDTH > 1) begin
                                        rx_shift_reg <= {miso, rx_shift_reg[DATA_WIDTH-1:1]};
                                    end else begin
                                        rx_shift_reg <= miso;
                                    end
                                end
                            end
                        end else if (sclk_gen == CPOL) begin
                            // Trailing edge - shift and present next transmit bit
                            if (bit_counter < DATA_WIDTH) begin
                                if (MSB_FIRST) begin
                                    if (DATA_WIDTH > 1) begin
                                        tx_shift_reg <= {tx_shift_reg[DATA_WIDTH-2:0], 1'b0};
                                        mosi <= tx_shift_reg[DATA_WIDTH-2];
                                    end else begin
                                        tx_shift_reg <= 1'b0;
                                        mosi <= 1'b0;
                                    end
                                end else begin
                                    if (DATA_WIDTH > 1) begin
                                        tx_shift_reg <= {1'b0, tx_shift_reg[DATA_WIDTH-1:1]};
                                        mosi <= tx_shift_reg[1];
                                    end else begin
                                        tx_shift_reg <= 1'b0;
                                        mosi <= 1'b0;
                                    end
                                end
                                bit_counter <= bit_counter + 1;
                            end
                        end
                    end
                end else begin
                    // Mode 1/3: sample on trailing edge, change data on leading edge.
                    if (sclk_gen != last_sclk) begin
                        if (sclk_gen == ~CPOL) begin // Leading edge - change data
                            if (bit_counter < DATA_WIDTH) begin
                                // Shift out transmitted data
                                if (MSB_FIRST) begin
                                    mosi <= tx_shift_reg[DATA_WIDTH-1];
                                    if (DATA_WIDTH > 1) begin
                                        tx_shift_reg <= {tx_shift_reg[DATA_WIDTH-2:0], 1'b0};
                                    end else begin
                                        tx_shift_reg <= 1'b0;  // For 1-bit, just set to 0 after transmission
                                    end
                                end else begin
                                    mosi <= tx_shift_reg[0];
                                    if (DATA_WIDTH > 1) begin
                                        tx_shift_reg <= {1'b0, tx_shift_reg[DATA_WIDTH-1:1]};
                                    end else begin
                                        tx_shift_reg <= 1'b0;  // For 1-bit, just set to 0 after transmission
                                    end
                                end
                                bit_counter <= bit_counter + 1;
                            end
                        end else if (sclk_gen == CPOL) begin // Trailing edge - sample data
                            if (bit_counter <= DATA_WIDTH && bit_counter > 0) begin
                                // Shift in received data
                                if (MSB_FIRST) begin
                                    if (DATA_WIDTH > 1) begin
                                        rx_shift_reg <= {rx_shift_reg[DATA_WIDTH-2:0], miso};
                                    end else begin
                                        rx_shift_reg <= miso;  // For 1-bit, just set to received bit
                                    end
                                end else begin
                                    if (DATA_WIDTH > 1) begin
                                        rx_shift_reg <= {miso, rx_shift_reg[DATA_WIDTH-1:1]};
                                    end else begin
                                        rx_shift_reg <= miso;  // For 1-bit, just set to received bit
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end

    // SCLK output assignment
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sclk <= CPOL;
        end else begin
            // Force protocol idle level whenever transfer is not active.
            sclk <= (state == TRANSMIT || state == RECEIVE) ? sclk_gen : CPOL;
        end
    end

    // Next state logic
    always @(*) begin
        next_state = state;

        case (state)
            IDLE: begin
                if (start_tx) begin
                    next_state = SETUP;
                end else if (start_rx) begin
                    next_state = SETUP;
                end
            end

            SETUP: begin
                next_state = TRANSMIT;
            end

            TRANSMIT: begin
                if (bit_counter >= DATA_WIDTH && sclk_gen == CPOL) begin
                    next_state = COMPLETE;
                end
            end

            RECEIVE: begin
                if (bit_counter >= DATA_WIDTH && sclk_gen == CPOL) begin
                    next_state = COMPLETE;
                end
            end

            COMPLETE: begin
                next_state = IDLE;
            end

            default: next_state = IDLE;
        endcase
    end

    // Output logic
    always @(*) begin
        case (state)
            IDLE: begin
                busy = 0;
                irq = 0;
                ss_n = {NUM_SLAVES{~SS_ACTIVE}};
            end

            SETUP: begin
                busy = 1;
                // Deterministic one-hot selection using SELECTED_SLAVE.
                ss_n = {NUM_SLAVES{~SS_ACTIVE}};
                ss_n[SELECTED_SLAVE_CLAMP] = SS_ACTIVE;
            end

            TRANSMIT: begin
                busy = 1;
                ss_n = {NUM_SLAVES{~SS_ACTIVE}};
                ss_n[SELECTED_SLAVE_CLAMP] = SS_ACTIVE;
            end

            RECEIVE: begin
                busy = 1;
                ss_n = {NUM_SLAVES{~SS_ACTIVE}};
                ss_n[SELECTED_SLAVE_CLAMP] = SS_ACTIVE;
            end

            COMPLETE: begin
                busy = 0;
                ss_n = {NUM_SLAVES{~SS_ACTIVE}};  // Deactivate slave select
                irq = 1;  // Generate interrupt
                rx_data = rx_shift_reg;  // Output received data
            end

            default: begin
                busy = 0;
                irq = 0;
                ss_n = {NUM_SLAVES{~SS_ACTIVE}};
            end
        endcase
    end

endmodule