# Intraday Momentum Trading Strategy Implementation

This project is an implementation of the intraday momentum-based trading strategy described in the paper:  
[Intraday Momentum Based Trading Strategy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284).

The primary goal of this project is to recreate and test the strategy for personal research purposes.

## Table of Contents

- [Overview](#overview)
- [Project Goals](#project-goals)
- [Architecture and Implementation](#architecture-and-implementation)
- [Database Integration](#database-integration)
- [Data Requirements](#data-requirements)
- [Installation and Setup](#installation-and-setup)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

This project implements a class-based system for testing the intraday momentum trading strategy. The design is structured to allow for clear testing and analysis, with an eye toward future enhancements such as an event-based backtest engine.

## Project Goals

- **Recreate and Test:** Validate the trading strategy described in the referenced paper.
- **Performance:** Leverage a QuestDB database to store and retrieve pre-calculated data, ensuring speed and efficiency.
- **Modularity:** Utilize a class-based design for ease of testing and maintenance.
- **Future Development:** Identify improvements, such as transitioning to an event-based backtest engine through the implementation of callback functions and an event bus.

## Architecture and Implementation

- **Class-based Design:** The current implementation uses object-oriented programming to structure the code into manageable classes.
- **Backtesting Engine:** Currently implemented as a class-based system. A future iteration will shift to an event-based architecture to allow for more flexible and dynamic backtesting.
- **Data Flow:** The strategy relies on pre-processed data stored in a QuestDB database to achieve rapid computation and efficient result times.

## Database Integration

The project connects to a QuestDB database where relevant data calculations have been performed. This approach is chosen to enhance the speed of computation and result delivery. Note that:
- The code does **not** include the data access layer for downloading, transforming, cleaning, or normalizing raw data.
- Users need to set up and populate the QuestDB database with the necessary pre-processed data.

## Data Requirements

To replicate performance and run the scripts successfully, the following data bars are expected:
- **Daily Bars**
- **Minute Bars**
- **5-Minute Bars**

**Note:**  
Data resampling should be performed in Pandas for efficiency. It is recommended not to perform resampling via SQL queries within QuestDB.

## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/intraday-momentum-strategy.git
   cd intraday-momentum-strategy
