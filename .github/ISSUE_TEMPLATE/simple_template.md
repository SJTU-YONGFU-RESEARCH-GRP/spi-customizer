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
    id: email
    attributes:
      label: Email Address
      description: "Your email address for receiving results"
      placeholder: "your-email@example.com"
    validations:
      required: true
---

## What Happens Next?

1. 🤖 The automation system will parse your configuration
2. 🔧 Custom Verilog code will be generated for your specifications
3. 🧪 The design will be tested with comprehensive testbenches
4. 📊 Timing diagrams and performance plots will be created
5. 📧 Results will be emailed to you with downloadable files
6. ✅ This issue will be updated with the results and then closed

**Expected completion time: 5-10 minutes**
