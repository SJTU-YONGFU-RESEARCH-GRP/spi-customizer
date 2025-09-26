---
name: SPI Configuration Request
description: Request a custom SPI (Serial Peripheral Interface) configuration
title: "SPI Config: [Brief description of your configuration]"
labels: ["spi-customization", "enhancement"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
## SPI Configuration Request

Please provide the following details for your custom SPI configuration:
  - type: input
    id: spi_mode
    attributes:
      label: SPI Mode
      description: "Enter the SPI mode (0, 1, 2, or 3)"
      placeholder: "0, 1, 2, or 3"
    validations:
      required: true
  - type: input
    id: clock_frequency
    attributes:
      label: Clock Frequency (MHz)
      description: "Target clock frequency in MHz"
      placeholder: "10, 25, 50, etc."
    validations:
      required: true
  - type: input
    id: data_width
    attributes:
      label: Data Width (bits)
      description: "Data width in bits"
      placeholder: "8, 16, 32, or custom"
    validations:
      required: true
  - type: input
    id: num_slaves
    attributes:
      label: Number of Slaves
      description: "Number of slave devices"
      placeholder: "1, 2, 4, 8, or custom"
    validations:
      required: false
  - type: checkboxes
    id: slave_behavior
    attributes:
      label: Slave Select Behavior
      description: "Choose the slave select behavior"
      options:
        - label: "Active Low (most common)"
          required: false
        - label: "Active High"
          required: false
  - type: checkboxes
    id: data_order
    attributes:
      label: Data Order
      description: "Choose the data transmission order"
      options:
        - label: "MSB First (most common)"
          required: false
        - label: "LSB First"
          required: false
  - type: checkboxes
    id: features
    attributes:
      label: Special Features
      description: "Select any special features needed"
      options:
        - label: "Interrupt Support"
          required: false
        - label: "FIFO Buffers"
          required: false
        - label: "DMA Support"
          required: false
        - label: "Multi-master Support"
          required: false
  - type: dropdown
    id: test_duration
    attributes:
      label: Test Duration
      description: "Choose the test duration level"
      options:
        - "Brief: Basic functionality tests (~1000 cycles)"
        - "Standard: Corner case testing (~10000 cycles)"
        - "Comprehensive: Full protocol validation (~50000 cycles)"
      default: 1
    validations:
      required: false
  - type: checkboxes
    id: test_options
    attributes:
      label: Testing Options
      description: "Select testing options"
      options:
        - label: "Clock Jitter Testing (tests timing margins)"
          required: false
        - label: "Waveform Capture (generates detailed timing diagrams)"
          required: false
  - type: input
    id: email
    attributes:
      label: Email Address
      description: "Your email address for receiving results"
      placeholder: "your-email@example.com"
    validations:
      required: true
  - type: input
    id: github_username
    attributes:
      label: GitHub Username
      description: "Your GitHub username for issue updates"
      placeholder: "your-username"
    validations:
      required: true
  - type: textarea
    id: additional_notes
    attributes:
      label: Additional Notes
      description: "Any additional requirements, constraints, or specific use cases"
      placeholder: "Provide any additional requirements, constraints, or specific use cases for this SPI configuration"
    validations:
      required: false
  - type: markdown
    attributes:
      value: |
---

## What Happens Next?

1. 🤖 The automation system will parse your configuration
2. 🔧 Custom Verilog code will be generated for your specifications
3. 🧪 The design will be tested with comprehensive testbenches
4. 📊 Timing diagrams and performance plots will be created
5. 📧 Results will be emailed to you with downloadable files
6. ✅ This issue will be updated with the results and then closed

**Expected completion time: 5-10 minutes**
