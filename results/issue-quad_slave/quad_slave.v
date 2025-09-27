module spi_master #(
    parameter MODE = 2,              // SPI Mode (0-3)
    parameter DATA_WIDTH = 16,       // Data width in bits
    parameter NUM_SLAVES = 4,        // Number of slave devices
    parameter SLAVE_ACTIVE_LOW = 1,  // Slave select active level
    parameter MSB_FIRST = 1,          // Data transmission order
    parameter FIFO_DEPTH = 16,        // FIFO buffer depth
    parameter CLOCK_DIVIDER = 2,  // System clock divider
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
    reg [4:0]  bit_counter;    // Bit transmission counter
    reg [DATA_WIDTH-1:0] tx_shift_reg;
    reg [DATA_WIDTH-1:0] rx_shift_reg;
    reg        sclk_gen;       // SCLK generator
    reg        last_sclk;      // Previous SCLK value for edge detection

    // Clock polarity and phase for different modes
    wire CPOL = (MODE == 2) || (MODE == 3);  // Clock polarity
    wire CPHA = (MODE == 1) || (MODE == 3);  // Clock phase

    // Slave select active level
    wire SS_ACTIVE = SLAVE_ACTIVE_LOW ? 1'b0 : 1'b1;

    // Default data generation
    reg [DATA_WIDTH-1:0] default_data;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            default_data <= DEFAULT_DATA_VALUE;
        end else if (DEFAULT_DATA_ENABLED) begin
            case (DEFAULT_DATA_PATTERN)
                "a5a5": default_data <= 16'hA5A5;
                "ffff": default_data <= 16'hFFFF;
                "0000": default_data <= 16'h0000;
                "5555": default_data <= 16'h5555;
                default: default_data <= DEFAULT_DATA_VALUE;
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
            ss_n <= {NUM_SLAVES{1'b1}};
            busy <= 0;
            irq <= 0;
            last_sclk <= CPOL;
        end else begin
            state <= next_state;
            last_sclk <= sclk_gen;

            // SCLK generation
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

            // Data transmission and reception
            if (state == TRANSMIT || state == RECEIVE) begin
                // Sample data on appropriate edge
                if (CPHA == 0) begin
                    // Sample on leading edge
                    if (sclk_gen != last_sclk && sclk_gen == ~CPOL) begin
                        if (bit_counter < DATA_WIDTH) begin
                            // Shift in received data
                            if (MSB_FIRST) begin
                                rx_shift_reg <= {rx_shift_reg[DATA_WIDTH-2:0], miso};
                            end else begin
                                rx_shift_reg <= {miso, rx_shift_reg[DATA_WIDTH-1:1]};
                            end

                            // Shift out transmitted data
                            if (MSB_FIRST) begin
                                mosi <= tx_shift_reg[DATA_WIDTH-1];
                                tx_shift_reg <= {tx_shift_reg[DATA_WIDTH-2:0], 1'b0};
                            end else begin
                                mosi <= tx_shift_reg[0];
                                tx_shift_reg <= {1'b0, tx_shift_reg[DATA_WIDTH-1:1]};
                            end

                            bit_counter <= bit_counter + 1;
                        end
                    end
                end else begin
                    // Sample on trailing edge
                    if (sclk_gen != last_sclk && sclk_gen == CPOL) begin
                        if (bit_counter < DATA_WIDTH) begin
                            // Shift in received data
                            if (MSB_FIRST) begin
                                rx_shift_reg <= {rx_shift_reg[DATA_WIDTH-2:0], miso};
                            end else begin
                                rx_shift_reg <= {miso, rx_shift_reg[DATA_WIDTH-1:1]};
                            end

                            // Shift out transmitted data
                            if (MSB_FIRST) begin
                                mosi <= tx_shift_reg[DATA_WIDTH-1];
                                tx_shift_reg <= {tx_shift_reg[DATA_WIDTH-2:0], 1'b0};
                            end else begin
                                mosi <= tx_shift_reg[0];
                                tx_shift_reg <= {1'b0, tx_shift_reg[DATA_WIDTH-1:1]};
                            end

                            bit_counter <= bit_counter + 1;
                        end
                    end
                end
            end
        end
    end

    // SCLK output assignment
    always @(posedge clk) begin
        sclk <= sclk_gen;
    end

    // Next state logic
    always @(*) begin
        next_state = state;

        case (state)
            IDLE: begin
                busy = 0;
                irq = 0;
                ss_n = {NUM_SLAVES{1'b1}};
                rx_data = 0;

                if (start_tx) begin
                    next_state = SETUP;
                end else if (start_rx) begin
                    next_state = SETUP;
                end
            end

            SETUP: begin
                busy = 1;
                ss_n = {NUM_SLAVES{SS_ACTIVE}};  // Activate slave select
                bit_counter = 0;
                tx_shift_reg = DEFAULT_DATA_ENABLED ? default_data : tx_data;
                rx_shift_reg = 0;
                next_state = TRANSMIT;
            end

            TRANSMIT: begin
                busy = 1;
                if (bit_counter >= DATA_WIDTH) begin
                    next_state = COMPLETE;
                end
            end

            RECEIVE: begin
                busy = 1;
                if (bit_counter >= DATA_WIDTH) begin
                    rx_data = rx_shift_reg;
                    next_state = COMPLETE;
                end
            end

            COMPLETE: begin
                busy = 0;
                ss_n = {NUM_SLAVES{1'b1}};  // Deactivate slave select
                irq = 1;  // Generate interrupt
                next_state = IDLE;
            end

            default: next_state = IDLE;
        endcase
    end

endmodule