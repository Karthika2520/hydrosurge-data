\\HydroSurge Data Dictionary

1\. Purpose



This document defines the data fields, units, timestamp conventions, quality indicators, and output contracts used by the HydroSurge data and geospatial pipeline.



The purpose is to ensure that all data sources are converted into a consistent, ready-to-consume representation before being passed to downstream rainfall prediction, flood/inundation modelling, and system integration components.



2\. Observation Schema



Schema file:



contracts/observation.schema.json



An observation represents a point-based measurement such as rainfall.



Field	Type	Description	Unit / Range

source	string	Name or identifier of the data source	Source identifier

variable	string	Observed environmental variable	Example: rainfall

value	number	Observed measurement value	Depends on variable

unit	string	Unit of the observed value	Example: mm

latitude	number	Latitude of observation location	-90 to 90

longitude	number	Longitude of observation location	-180 to 180

observed\_at	date-time	Time at which the observation occurred	ISO-8601 UTC

received\_at	date-time	Time at which the system received the observation	ISO-8601 UTC

quality\_score	number	Normalized source/data quality score	0 to 1

Example

{

&#x20; "source": "mock-csv",

&#x20; "variable": "rainfall",

&#x20; "value": 12.5,

&#x20; "unit": "mm",

&#x20; "latitude": 13.0827,

&#x20; "longitude": 80.2707,

&#x20; "observed\_at": "2024-09-01T06:00:00Z",

&#x20; "received\_at": "2024-09-01T06:05:00Z",

&#x20; "quality\_score": 1.0

}

3\. Raster Schema



Schema file:



contracts/raster.schema.json



A raster represents gridded spatial data such as rainfall surfaces, DEMs, or reference layers.



Field	Type	Description	Unit / Range

source	string	Name or identifier of the raster source	Source identifier

variable	string	Variable represented by the raster	Example: rainfall

valid\_time	date-time	Time represented by the raster	ISO-8601 UTC

crs	string	Coordinate Reference System	Example: EPSG:4326

resolution\_m	number	Raster spatial resolution	metres, > 0

bbox	array	Bounding box of raster extent	Four numeric coordinates

nodata	number/null	Value representing missing raster cells	Source-dependent

quality\_score	number	Normalized raster quality score	0 to 1

file\_uri	string	Location of the raster file	File URI/path

Example

{

&#x20; "source": "mock-raster",

&#x20; "variable": "rainfall",

&#x20; "valid\_time": "2024-09-01T06:00:00Z",

&#x20; "crs": "EPSG:4326",

&#x20; "resolution\_m": 1000.0,

&#x20; "bbox": \[80.25, 13.05, 80.30, 13.10],

&#x20; "nodata": -9999,

&#x20; "quality\_score": 1.0,

&#x20; "file\_uri": "data/processed/resampled\_rainfall.tif"

}

4\. Rainfall Output Schema



Schema file:



contracts/rainfall\_output.schema.json



This contract defines the rainfall prediction output passed to downstream components.



Field	Type	Description	Unit / Range

tile\_id	string	Spatial tile identifier	Tile identifier

timestamp	date-time	Prediction timestamp	ISO-8601 UTC

rainfall\_mm\_hr	number	Predicted rainfall intensity	mm/hour

confidence	number	Prediction confidence	0 to 1

Example

{

&#x20; "tile\_id": "tile-001",

&#x20; "timestamp": "2024-09-01T06:00:00Z",

&#x20; "rainfall\_mm\_hr": 18.5,

&#x20; "confidence": 0.92

}

5\. Inundation Output Schema



Schema file:



contracts/inundation\_output.schema.json



This contract defines the flood/inundation prediction output.



Field	Type	Description	Unit / Range

tile\_id	string	Spatial tile identifier	Tile identifier

timestamp	date-time	Prediction timestamp	ISO-8601 UTC

flood\_probability	number	Probability of flooding	0 to 1

depth\_band	string	Predicted inundation depth category	Category

confidence	number	Prediction confidence	0 to 1

Example

{

&#x20; "tile\_id": "tile-001",

&#x20; "timestamp": "2024-09-01T06:00:00Z",

&#x20; "flood\_probability": 0.78,

&#x20; "depth\_band": "0.3-1.0m",

&#x20; "confidence": 0.87

}

6\. Timestamp Conventions



The system distinguishes between different meanings of time.



observed\_at



The actual time represented by an observation.



received\_at



The time when the system received the observation.



valid\_time



The time represented by a raster product.



timestamp



The timestamp associated with a prediction output.



All normalized timestamps use ISO-8601 UTC notation and end with Z.



The system preserves the difference between observation time and reception time so that source latency can be measured.



7\. Time Alignment



Normalized observations are sorted by observed\_at.



The temporal normalization process:



Reads the normalized observation dataset.

Parses observed\_at and received\_at.

Converts timestamps to timezone-aware UTC.

Converts UTC timestamps to ISO-8601 strings ending in Z.

Sorts observations by observed\_at.

Preserves the original measurement values and locations.



No timestamps are invented or silently filled.



For each valid observation:



observed\_at <= received\_at



8\. Spatial Conventions

Coordinate Reference System



The working CRS for the current mock pipeline is:



EPSG:4326



The CRS is explicitly retained in raster metadata.



Coordinates



Point observations use:



latitude

longitude



Latitude range:



\-90 to 90



Longitude range:



\-180 to 180



Raster Resolution



Raster resolution is represented using:



resolution\_m



The native raster resolution is preserved during normalization where applicable.



When resampling is required, the target resolution is explicitly specified.



The current deterministic resampling example uses:



1000 metres



Spatial Alignment



Rasters used together in downstream processing must have compatible:



CRS

transform

width

height

spatial extent

nodata handling



The spatial alignment step uses a reference raster to create a compatible raster grid.



9\. Missing Data and NoData



Missing observations are not silently replaced.



For observations, required fields must be present and non-empty.



For rasters, missing cells are represented using the raster's declared nodata value.



Current mock raster nodata value:



\-9999



Long missing gaps must not be silently interpolated.



Any interpolation or gap filling must be explicitly justified and recorded.



10\. Quality Indicators



The data quality pipeline produces the following indicators.



Completeness



Measures the proportion of observations containing all required fields.



completeness = complete\_observations / total\_observations



Range: 0 to 1



Range Validity



Checks whether observations contain physically and structurally valid values.



The current implementation checks:



latitude

longitude

measurement value

quality score



Range validity is represented as a value between 0 and 1.



Duplicate Rate



Measures the proportion of duplicate observations.



Duplicate identity is based on:



source

variable

latitude

longitude

observed\_at



Lower duplicate rate is better.



Source Latency



Source latency measures the difference between reception time and observation time.



latency = received\_at - observed\_at



The quality report stores the average latency in seconds.



Source Quality Score



quality\_score is normalized between 0 and 1.



Higher values indicate better source/data quality.



Fallback State



The quality pipeline reports a source state:



primary

degraded

fallback

11\. Source Quality Assessment



The source quality assessment combines multiple quality indicators into a heuristic overall quality score.



The current implementation uses:



overall\_quality = 0.30 \* completeness + 0.25 \* range\_validity + 0.15 \* (1 - duplicate\_rate) + 0.15 \* latency\_score + 0.15 \* source\_quality\_score



Latency quality is calculated as:



latency\_score = 1 / (1 + average\_latency\_seconds / 300)



The overall quality score is bounded between 0 and 1.



Fallback thresholds

Overall quality	State

>= 0.80	primary

>= 0.50 and < 0.80	degraded

< 0.50	fallback



These thresholds are heuristic implementation rules and are not presented as calibrated probabilities.



12\. Provenance



Source provenance is recorded in:



data/manifests/source\_manifest.json



The manifest records:



source identifier

source type

source format

variable

status

URI/path

native resolution

timestamp fields

source notes

Current mock source

source: mock-csv

type: observation

format: CSV

variable: rainfall

status: proxy



The mock source is deterministic and is used for development and contract validation.



It is not represented as a production live data source.



13\. Normalized Data Artifacts

Normalized observations



data/processed/normalized\_observations.json



Contains observations converted into the standard Observation contract.



Temporally normalized observations



data/processed/temporal\_normalized\_observations.json



Contains observations with UTC-normalized timestamps and deterministic ordering.



Normalized rainfall raster



data/processed/normalized\_rainfall.tif



Contains raster data normalized to the declared CRS.



Resampled rainfall raster



data/processed/resampled\_rainfall.tif



Contains rainfall raster data resampled to the requested target resolution.



Spatially aligned rainfall raster



data/processed/aligned\_rainfall.tif



Contains rainfall raster data aligned to the reference raster grid.



14\. Data Processing Flow

RAW SOURCE

&#x20;   |

&#x20;   v

SOURCE ADAPTER

&#x20;   |

&#x20;   v

NORMALIZED REPRESENTATION

&#x20;   |

&#x20;   +----------------------+

&#x20;   |                      |

&#x20;   v                      v

TEMPORAL NORMALIZATION   RASTER NORMALIZATION

&#x20;   |                      |

&#x20;   |                      v

&#x20;   |                  RESAMPLING

&#x20;   |                      |

&#x20;   |                      v

&#x20;   |                  SPATIAL ALIGNMENT

&#x20;   |                      |

&#x20;   +----------+-----------+

&#x20;              |

&#x20;              v

&#x20;       QUALITY ASSESSMENT

&#x20;              |

&#x20;              v

&#x20;      READY-TO-CONSUME DATA

&#x20;              |

&#x20;              v

&#x20;     DOWNSTREAM R\&D MODULES



The adapter layer converts source-specific formats into the common representation.



The preprocessing layer handles temporal, CRS, resolution, and spatial normalization.



The quality layer calculates data quality and fallback information.



15\. Contract Validation



All contract examples and mock provider payloads must conform to their corresponding JSON schemas.



Contract files:



contracts/observation.schema.json

contracts/raster.schema.json

contracts/rainfall\_output.schema.json

contracts/inundation\_output.schema.json



Mock payloads:



providers/mock/observation.json

providers/mock/raster.json

providers/mock/rainfall\_output.json

providers/mock/inundation\_output.json



Schema validation is performed before contract freeze.



16\. Reproducibility



The data pipeline is designed to produce deterministic results from deterministic mock inputs.



Reproducibility includes:



deterministic mock observations

deterministic mock raster

explicit CRS

explicit raster resolution

explicit nodata handling

deterministic timestamp normalization

deterministic spatial alignment

deterministic quality calculations

version-controlled schemas

source provenance manifest

automated tests



The processing functions do not silently introduce missing timestamps, coordinates, or measurements.



17\. Current Project Status



The following implementation components are currently available:



adapters/

&#x20;   csv\_observation\_adapter.py



preprocessing/

&#x20;   raster\_normalizer.py

&#x20;   raster\_resampler.py

&#x20;   spatial\_aligner.py

&#x20;   temporal\_normalizer.py



quality/

&#x20;   observation\_quality.py

&#x20;   source\_quality.py



contracts/

&#x20;   observation.schema.json

&#x20;   raster.schema.json

&#x20;   rainfall\_output.schema.json

&#x20;   inundation\_output.schema.json



providers/mock/

&#x20;   observation.json

&#x20;   raster.json

&#x20;   rainfall\_output.json

&#x20;   inundation\_output.json



data/manifests/

&#x20;   source\_manifest.json



data/processed/

&#x20;   normalized\_observations.json

&#x20;   temporal\_normalized\_observations.json

&#x20;   normalized\_rainfall.tif

&#x20;   resampled\_rainfall.tif

&#x20;   aligned\_rainfall.tif



results/

&#x20;   quality\_report.json

&#x20;   source\_quality\_report.json



The implementation is validated through the automated test suite.



Final schema validation against mock and downstream sample outputs remains part of the component-ready delivery process.



18\. Handoff Information

R\&D-1



Provides:



ready-to-train rainfall dataset

exact feature meanings

time alignment rule

R\&D-2



Provides:



aligned rainfall/reference raster data

rainfall input contract

CRS and resolution metadata

R\&D-4



Provides:



JSON schema files

mock JSON payloads

contract validation command

Presentation / Documentation



The provenance summary should identify:



source

source status

native resolution

normalized resolution

timestamp handling

source latency

known limitations



Current mock source status:



proxy



It should not be presented as a live production source.

19\. Contract Freeze



Schema changes should be avoided after the contract freeze.



If a source requires a different input format, the preferred approach is to update or add an adapter rather than changing the shared downstream contract.



Every schema change must also update:



DATA\_DICTIONARY.md

corresponding sample JSON

contract validation tests



The target contract version for delivery is:



schema-v1



Final schema validation and contract freeze remain required before delivery.

