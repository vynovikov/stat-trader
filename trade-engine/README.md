# ML Trading Pattern Analysis

This project aims to discover and analyze significant price movements in cryptocurrency markets using machine learning techniques. The main goal is to identify recurring patterns that precede significant price movements through unsupervised learning and clustering.

## Project Overview

The analysis process consists of three main stages:

1. **Data Preparation** (`preprocessor/`)
   - Adding technical indicators (Moving Averages, etc.)
   - Cleaning and formatting the data
   - Ensuring data completeness

2. **Pattern Marking** (`marker/`)
   - Identifying significant price movements in historical data
   - Extracting "prelude" patterns that precede these movements
   - Segmenting the data into analyzable chunks

3. **Pattern Analysis** (`vectorizer/`)
   - Converting prelude patterns into vector representations
   - Clustering similar patterns in vector space
   - Identifying recurring market configurations

## Key Components

### Preprocessor
Handles data preparation and feature engineering:
- Adding technical indicators
- Cleaning incomplete data
- Preparing data for analysis

### Marker
Identifies significant market movements and their preceding patterns:
- Detects trending movements using price action rules
- Extracts "prelude" configurations (preceding candles)
- Marks significant movements based on average volatility

### Vectorizer
Transforms market patterns into analyzable vector form:
- Converts price action patterns into vectors
- Prepares data for clustering analysis
- Handles feature selection and normalization

## Project Goals

1. Identify only significant price movements (filtered by volatility and trend strength)
2. Extract and analyze patterns that precede these movements
3. Find natural clusters of similar prelude patterns in vector space
4. Discover recurring market configurations that may have predictive value

## Data Structure

The project works with candlestick data in the following format:
- OHLCV data (Open, High, Low, Close, Volume)
- Technical indicators (Moving Averages)
- Custom pattern markers and segments

## Usage

[TODO: Add usage instructions and examples]

# ML Trading Pattern Analysis

This project aims to discover and analyze significant price movements in cryptocurrency markets using machine learning techniques. The main goal is to identify recurring patterns that precede significant price movements through unsupervised learning and clustering.

## Project Overview

The analysis process consists of three main stages:

1. **Data Preparation** (`preprocessor/`)
   - Adding technical indicators (Moving Averages, etc.)
   - Cleaning and formatting the data
   - Ensuring data completeness

2. **Pattern Marking** (`marker/`)
   - Identifying significant price movements in historical data
   - Extracting "prelude" patterns that precede these movements
   - Segmenting the data into analyzable chunks

3. **Pattern Analysis** (`vectorizer/`)
   - Converting prelude patterns into vector representations
   - Clustering similar patterns in vector space
   - Identifying recurring market configurations

## Key Components

### Preprocessor
Handles data preparation and feature engineering:
- Adding technical indicators
- Cleaning incomplete data
- Preparing data for analysis

### Marker
Identifies significant market movements and their preceding patterns:
- Detects trending movements using price action rules
- Extracts "prelude" configurations (preceding candles)
- Marks significant movements based on average volatility

### Vectorizer
Transforms market patterns into analyzable vector form:
- Converts price action patterns into vectors
- Prepares data for clustering analysis
- Handles feature selection and normalization

### Pattern Analysis Corruption Detection

The pattern analysis includes a sophisticated corruption detection mechanism that helps identify and filter out unreliable pattern formations. This is crucial for maintaining the quality of the analysis and avoiding false signals.

#### Dynamic Group Reconstruction

The corruption detection mechanism plays a crucial role in dynamic pattern analysis when new points appear on the chart:

1. **Group Extension**
   - When a new point appears with the same direction as the group
   - If it's a valid neighbor (within radius and sector)
   - The group can be extended to include this point

2. **Group Corruption**
   - When a new point appears with opposite direction
   - It can "corrupt" existing group points if it falls within their ±90° sectors
   - This triggers group reconstruction:
     - Corrupted points are removed from the group
     - The group may split or disappear entirely
     - Remaining valid points may form new groups

3. **Real-time Pattern Validation**
   - Groups are continuously validated as new points appear
   - Strong patterns survive opposing neighbors
   - Weak or false patterns are naturally filtered out

This dynamic reconstruction ensures that only stable and reliable patterns are maintained, while quickly adapting to changing market conditions.

#### Corruption Detection Logic

A pattern point is marked as "corrupted" when:
1. It has neighboring points with opposite directions within its ±90° sectors
2. The angular relationship between neighbors creates conflicting trend signals

Key concepts:
- **Direction**: Each point has a direction (UP/DOWN) representing the trend
- **Corruption Angles**: Track the angular range where opposite-direction neighbors are found
  - `corruption_angle_start`: Beginning of the corrupted sector
  - `corruption_angle_end`: End of the corrupted sector
- **Sector Size**: Points are grouped into sectors (default 6°) for efficient neighbor analysis

#### Examples of Corruption

1. **Direct Conflict**
   - UP point with DOWN neighbor at 0° (same direction)
   - Results in immediate corruption

2. **Sector Conflict**
   - UP point with:
     - UP neighbor at +30°
     - DOWN neighbor at -30°
   - Corrupted due to opposite directions within ±90°

3. **Clean Pattern**
   - UP point with:
     - UP neighbor at +30°
     - DOWN neighbor at +150° (outside ±90°)
   - Not corrupted, directions don't conflict

This corruption detection helps:
- Filter out unreliable pattern formations