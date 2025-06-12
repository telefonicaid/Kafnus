Streetlight = {
    "entities": [
        {
            "id": "ENT-LUM-001", "type": "Streetlight",
            "TimeInstant": {"value": "2025-01-01T05:15:00.000Z", "type": "DateTime"},
            "location": {"value": {"type": "Point", "coordinates": [-0.350063, 40.054448]}, "type": "geo:json"},
            "polygon":{"value":  {"type":"Polygon", "coordinates":[[[-6.007389128,37.410871002],[-6.008284986,37.411015874],[-6.008400321,37.410894437],[-6.008620262,37.41003372],[-6.008488834,37.409669404],[-6.007759273,37.40953092],[-6.007389128,37.410871002]]]}, "type": "geo:json"},
            "route": {"value": {"type": "LineString","coordinates": [[-3.70256, 40.4165],[-3.70300, 40.4178],[-3.70412, 40.4190]]}, "type": "geo:json"},
            "stations": {"value": {"type": "MultiPoint","coordinates": [[-0.350063, 40.054448], [-0.351200, 40.055600],[-0.349000, 40.053000]]},"type": "geo:json"},
            "metroLines": {"value": {"type": "MultiLineString","coordinates": [[[-3.698, 40.410], [-3.695, 40.412], [-3.692, 40.414]], [[-3.700, 40.415], [-3.702, 40.418], [-3.705, 40.420]]]}, "type": "geo:json"},
            "districts": {"value": {"type": "MultiPolygon", "coordinates": [[[[ -3.70, 40.42 ], [ -3.71, 40.43 ], [ -3.69, 40.44 ], [ -3.70, 40.42 ]]],[[[ -3.72, 40.40 ], [ -3.73, 40.41 ], [ -3.71, 40.39 ], [ -3.72, 40.40 ]]]]},"type": "geo:json"},
            "mixedFeatures": {"value": {"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [-0.351, 40.055]},{"type": "LineString", "coordinates": [[-0.352,40.056], [-0.353,40.057]]}]}, "type": "geo:json"},
            "address": {"value": "Calle Honorato Ros, 9. 12230 Argelita, Castellón", "type": "Text"},
            "illuminanceLevel": {"value": 0.5, "type": "Number"},
            "enableHistoricCommand": {"value": True, "type": "Boolean"},
            "variables": {"value": {"duration": "20 days"}, "type":"jsonb"},
            "fixtureConfiguration": {"value": { "modes": ["high-efficiency", "dynamic-color"], "sensors": {"motion": True, "ambient_light": False}, "zigbee_channel": 25},"type": "json"},
            "maintainerEmail": {"value": "@telefonica.com", "type": "TextUnrestricted"},
            "lumensAdjustment": {"value": 15, "type": "Number"},
            "fixtureModelId": {"value": 2147483647, "type": "Number"},
            "ledCount": {"value": 922337203685, "type": "Number"},
            "wattageConsumption": {"value": 1.989e30, "type": "Number"},
            "colorTempKelvin": {"value": 4000.1234, "type": "Number"},
            "beamAngle": {"value": 30.75, "type": "Number"},
            "luminousEfficacy": {"value": 6.5e39, "type": "Number"},
            "installationId": {"value": 10001, "type": "Number"},
            "compatibleFixtures": {"value": ["STL-Gamma", "STL-Omega", "STL-Nova"], "type": "json"},
            "dimmingLevels": {"value": [10, 25, 50, 75, 100], "type": "json"},
            "temperatureRangeK": {"value": [2700, 3000, 4000, 5000, 6500], "type": "json"}
        }
    ],
    "subscriptions": {
        "historic": {
            "description": "Streetlight:HISTORIC:lighting:historic",
            "status": "active",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Streetlight"
                    }
                ],
                "condition": {
                    "attrs": [
                        "TimeInstant"
                    ]
                }
            },
            "notification": {
                "mqttCustom": {
                    "url": "mqtt://mosquitto:1883",
                    "topic": "kafnus/${service}${servicePath}/raw_historic"
                },
                "attrs": [
                    "TimeInstant",
                    "location",
                    "address",
                    "illuminanceLevel",
                    "enableHistoricCommand",
                    "variables",
                    "fixtureConfiguration",
                    "maintainerEmail",
                    "lumensAdjustment",
                    "fixtureModelId",
                    "ledCount",
                    "wattageConsumption",
                    "colorTempKelvin",
                    "beamAngle",
                    "luminousEfficacy",
                    "installationId",
                    "compatibleFixtures",
                    "dimmingLevels",
                    "temperatureRangeK"
                ]
            }
        },
        "lastdata": {
            "description": "Streetlight:LASTDATA:lighting:lastdata",
            "status": "active",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Streetlight"
                    }
                ],
                "condition": {
                    "attrs": [
                        "TimeInstant",
                        "location",
                        "address",
                        "illuminanceLevel",
                        "enableHistoricCommand",
                        "variables",
                        "fixtureConfiguration",
                        "maintainerEmail",
                        "lumensAdjustment",
                        "fixtureModelId",
                        "ledCount",
                        "wattageConsumption",
                        "colorTempKelvin",
                        "beamAngle",
                        "luminousEfficacy",
                        "installationId",
                        "compatibleFixtures",
                        "dimmingLevels",
                        "temperatureRangeK"
                    ],
                    "alterationTypes": [
                        "entityUpdate",
                        "entityCreate",
                        "entityDelete"
                    ]
                }
            },
            "notification": {
                "mqttCustom": {
                    "url": "mqtt://mosquitto:1883",
                    "topic": "kafnus/${service}${servicePath}/raw_lastdata"
                },
                "attrs": [
                    "TimeInstant",
                    "location",
                    "address",
                    "illuminanceLevel",
                    "enableHistoricCommand",
                    "variables",
                    "fixtureConfiguration",
                    "maintainerEmail",
                    "lumensAdjustment",
                    "fixtureModelId",
                    "ledCount",
                    "wattageConsumption",
                    "colorTempKelvin",
                    "beamAngle",
                    "luminousEfficacy",
                    "installationId",
                    "compatibleFixtures",
                    "dimmingLevels",
                    "temperatureRangeK"
                ]
            }
        },
        "mutable": {
            "description": "Streetlight:HISTORIC_MUTABLE:devices:historic_mutable",
            "status": "active",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Streetlight"
                    }
                ],
                "condition": {
                    "attrs": [
                        "TimeInstant",
                        "location",
                        "address",
                        "illuminanceLevel",
                        "enableHistoricCommand",
                        "variables",
                        "fixtureConfiguration",
                        "maintainerEmail",
                        "lumensAdjustment",
                        "fixtureModelId",
                        "ledCount",
                        "wattageConsumption",
                        "colorTempKelvin",
                        "beamAngle",
                        "luminousEfficacy",
                        "installationId",
                        "compatibleFixtures",
                        "dimmingLevels",
                        "temperatureRangeK"
                    ],
                    "alterationTypes": [
                        "entityUpdate",
                        "entityCreate",
                        "entityDelete"
                    ]
                }
            },
            "notification": {
                "mqttCustom": {
                    "url": "mqtt://mosquitto:1883",
                    "topic": "kafnus/${service}${servicePath}/raw_mutable"
                },
                "attrs": [
                    "TimeInstant",
                    "location",
                    "address",
                    "illuminanceLevel",
                    "enableHistoricCommand",
                    "variables",
                    "fixtureConfiguration",
                    "maintainerEmail",
                    "lumensAdjustment",
                    "fixtureModelId",
                    "ledCount",
                    "wattageConsumption",
                    "colorTempKelvin",
                    "beamAngle",
                    "luminousEfficacy",
                    "installationId",
                    "compatibleFixtures",
                    "dimmingLevels",
                    "temperatureRangeK"
                ]
            }
        },
    },
    "updateEntities": [
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:15:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350063,
                        40.054448
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 9. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.5,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": True,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "20 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "high-efficiency",
                        "dynamic-color"
                    ],
                    "sensors": {
                        "motion": True,
                        "ambient_light": False
                    },
                    "zigbee_channel": 25
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 15,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483647,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203685,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.989e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4000.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 30.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 6.5e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10001,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Gamma",
                    "STL-Omega",
                    "STL-Nova"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    10,
                    25,
                    50,
                    75,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    2700,
                    3000,
                    4000,
                    5000,
                    6500
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:20:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350163,
                        40.054548
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 10. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.6,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": False,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "21 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "high-efficiency",
                        "dynamic-color",
                        "eco-mode"
                    ],
                    "sensors": {
                        "motion": False,
                        "ambient_light": True
                    },
                    "zigbee_channel": 26
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "soporte_tecnico@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 16,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483648,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203686,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.990e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4100.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 31.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 6.6e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10002,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Gamma",
                    "STL-Omega",
                    "STL-Nova",
                    "STL-Quantum"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    15,
                    30,
                    55,
                    80,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    2750,
                    3100,
                    4100,
                    5100,
                    6600
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:25:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350263,
                        40.054648
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 11. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.7,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": True,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "22 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "high-efficiency"
                    ],
                    "sensors": {
                        "motion": True,
                        "ambient_light": False
                    },
                    "zigbee_channel": 27
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "asistencia@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 17,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483649,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203687,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.991e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4200.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 32.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 6.7e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10003,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Gamma",
                    "STL-Omega"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    20,
                    35,
                    60,
                    85,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    2800,
                    3200,
                    4200,
                    5200,
                    6700
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:30:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350363,
                        40.054748
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 12. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.8,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": False,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "23 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "dynamic-color"
                    ],
                    "sensors": {
                        "motion": False,
                        "ambient_light": True
                    },
                    "zigbee_channel": 28
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "soporte@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 18,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483650,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203688,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.992e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4300.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 33.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 6.8e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10004,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Nova",
                    "STL-Quantum"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    25,
                    40,
                    65,
                    90,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    2850,
                    3300,
                    4300,
                    5300,
                    6800
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:35:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350463,
                        40.054848
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 13. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.9,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": True,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "24 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "high-efficiency",
                        "eco-mode"
                    ],
                    "sensors": {
                        "motion": True,
                        "ambient_light": True
                    },
                    "zigbee_channel": 29
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "tecnico@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 19,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483651,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203689,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.993e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4400.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 34.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 6.9e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10005,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Omega",
                    "STL-Nova"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    30,
                    45,
                    70,
                    95,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    2900,
                    3400,
                    4400,
                    5400,
                    6900
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:40:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350563,
                        40.054948
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 14. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 1.0,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": False,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "25 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "dynamic-color",
                        "eco-mode"
                    ],
                    "sensors": {
                        "motion": False,
                        "ambient_light": False
                    },
                    "zigbee_channel": 30
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "asistencia_tecnica@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 20,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483652,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203690,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.994e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4500.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 35.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 7.0e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10006,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Gamma",
                    "STL-Quantum"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    35,
                    50,
                    75,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    2950,
                    3500,
                    4500,
                    5500,
                    7000
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:45:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350663,
                        40.055048
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 15. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.4,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": True,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "26 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "high-efficiency"
                    ],
                    "sensors": {
                        "motion": True,
                        "ambient_light": True
                    },
                    "zigbee_channel": 31
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "soporte_luminica@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 21,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483653,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203691,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.995e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4600.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 36.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 7.1e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10007,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Omega",
                    "STL-Quantum"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    40,
                    55,
                    80,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    3000,
                    3600,
                    4600,
                    5600,
                    7100
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:50:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350763,
                        40.055148
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 16. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.3,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": False,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "27 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "dynamic-color"
                    ],
                    "sensors": {
                        "motion": False,
                        "ambient_light": False
                    },
                    "zigbee_channel": 32
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "mantenimiento@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 22,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483654,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203692,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.996e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4700.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 37.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 7.2e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10008,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Nova"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    45,
                    60,
                    85,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    3050,
                    3700,
                    4700,
                    5700,
                    7200
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T05:55:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350863,
                        40.055248
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 17. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.2,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": True,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "28 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "eco-mode"
                    ],
                    "sensors": {
                        "motion": True,
                        "ambient_light": False
                    },
                    "zigbee_channel": 33
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "soporte_iluminacion@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 23,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483655,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203693,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.997e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4800.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 38.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 7.3e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10009,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Gamma",
                    "STL-Omega",
                    "STL-Nova",
                    "STL-Quantum",
                    "STL-Alpha"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    50,
                    65,
                    90,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    3100,
                    3800,
                    4800,
                    5800,
                    7300
                ],
                "type": "json"
            }
        },
        {
            "id": "ENT-LUM-001",
            "type": "Streetlight",
            "TimeInstant": {
                "value": "2025-01-01T06:00:00.000Z",
                "type": "DateTime"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [
                        -0.350963,
                        40.055348
                    ]
                },
                "type": "geo:json"
            },
            "address": {
                "value": "Calle Honorato Ros, 18. 12230 Argelita, Castell�n",
                "type": "Text"
            },
            "illuminanceLevel": {
                "value": 0.1,
                "type": "Number"
            },
            "enableHistoricCommand": {
                "value": False,
                "type": "Boolean"
            },
            "variables": {
                "value": {
                    "duration": "29 days"
                },
                "type": "jsonb"
            },
            "fixtureConfiguration": {
                "value": {
                    "modes": [
                        "high-efficiency",
                        "dynamic-color",
                        "eco-mode"
                    ],
                    "sensors": {
                        "motion": False,
                        "ambient_light": True
                    },
                    "zigbee_channel": 34
                },
                "type": "json"
            },
            "maintainerEmail": {
                "value": "ayuda@telefonica.com",
                "type": "TextUnrestricted"
            },
            "lumensAdjustment": {
                "value": 24,
                "type": "Number"
            },
            "fixtureModelId": {
                "value": 2147483656,
                "type": "Number"
            },
            "ledCount": {
                "value": 922337203694,
                "type": "Number"
            },
            "wattageConsumption": {
                "value": 1.998e30,
                "type": "Number"
            },
            "colorTempKelvin": {
                "value": 4900.1234,
                "type": "Number"
            },
            "beamAngle": {
                "value": 39.75,
                "type": "Number"
            },
            "luminousEfficacy": {
                "value": 7.4e39,
                "type": "Number"
            },
            "installationId": {
                "value": 10010,
                "type": "Number"
            },
            "compatibleFixtures": {
                "value": [
                    "STL-Quantum"
                ],
                "type": "json"
            },
            "dimmingLevels": {
                "value": [
                    55,
                    70,
                    95,
                    100
                ],
                "type": "json"
            },
            "temperatureRangeK": {
                "value": [
                    3150,
                    3900,
                    4900,
                    5900,
                    7400
                ],
                "type": "json"
            }
        }
    ]
}