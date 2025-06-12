WasteContainer = {
    "entities": [
        {
            "id": "ENT-LUM-001", "type": "Streetlight",
            "TimeInstant": {"value": "2025-01-01T05:15:00.000Z", "type": "DateTime"},
            "location": {"value": {"type": "Point", "coordinates": [-0.350063, 40.054448]}, "type": "geo:json"},
            "polygon": {"value": {"type": "Polygon", "coordinates": [
                [[-6.007389128, 37.410871002], [-6.008284986, 37.411015874], [-6.008400321, 37.410894437],
                 [-6.008620262, 37.41003372], [-6.008488834, 37.409669404], [-6.007759273, 37.40953092],
                 [-6.007389128, 37.410871002]]]}, "type": "geo:json"},
            "route": {"value": {"type": "LineString",
                                "coordinates": [[-3.70256, 40.4165], [-3.70300, 40.4178], [-3.70412, 40.4190]]},
                      "type": "geo:json"},
            "stations": {"value": {"type": "MultiPoint", "coordinates": [[-0.350063, 40.054448], [-0.351200, 40.055600],
                                                                         [-0.349000, 40.053000]]}, "type": "geo:json"},
            "metroLines": {"value": {"type": "MultiLineString",
                                     "coordinates": [[[-3.698, 40.410], [-3.695, 40.412], [-3.692, 40.414]],
                                                     [[-3.700, 40.415], [-3.702, 40.418], [-3.705, 40.420]]]},
                           "type": "geo:json"},
            "districts": {"value": {"type": "MultiPolygon",
                                    "coordinates": [[[[-3.70, 40.42], [-3.71, 40.43], [-3.69, 40.44], [-3.70, 40.42]]],
                                                    [[[-3.72, 40.40], [-3.73, 40.41], [-3.71, 40.39],
                                                      [-3.72, 40.40]]]]}, "type": "geo:json"},
            "mixedFeatures": {"value": {"type": "GeometryCollection",
                                        "geometries": [{"type": "Point", "coordinates": [-0.351, 40.055]},
                                                       {"type": "LineString",
                                                        "coordinates": [[-0.352, 40.056], [-0.353, 40.057]]}]},
                              "type": "geo:json"},
            "address": {"value": "Calle Honorato Ros, 9. 12230 Argelita, Castellón", "type": "Text"},
            "illuminanceLevel": {"value": 0.5, "type": "Number"},
            "enableHistoricCommand": {"value": True, "type": "Boolean"},
            "variables": {"value": {"duration": "20 days"}, "type": "jsonb"},
            "fixtureConfiguration": {"value": {"modes": ["high-efficiency", "dynamic-color"],
                                               "sensors": {"motion": True, "ambient_light": False},
                                               "zigbee_channel": 25}, "type": "json"},
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
            "documentation": "Subscripción del flujo historic (tipo FLOW_HISTORIC) en modelo WasteContainer",
            "description": "WasteContainer:HISTORIC:lighting:historic",
            "status": "active",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "WasteContainer"
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
                    "fillLevel",
                    "containerStatus",
                    "wasteType",
                    "temperature",
                    "lastCollection",
                    "containerConfiguration",
                    "maintenanceSchedule",
                    "collectionRouteId",
                    "batteryLevel",
                    "odorLevel",
                    "fireRiskIndex",
                    "compactionCycles","containerWeight",
                    "supportedWasteTypes",
                    "collectionHistory",
                    "maintainerEmail"
                ]
            }
        },
        "lastdata": {
            "documentation": "Subscripción del flujo lastdata (tipo FLOW_LASTDATA) en modelo WasteContainer",
            "description": "WasteContainer:LASTDATA:lighting:lastdata",
            "status": "active",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "WasteContainer"
                    }
                ],
                "condition": {
                    "attrs": [
                        "TimeInstant",
                        "location",
                        "address",
                        "fillLevel",
                        "containerStatus",
                        "wasteType",
                        "temperature",
                        "lastCollection",
                        "containerConfiguration",
                        "maintenanceSchedule",
                        "collectionRouteId",
                        "batteryLevel",
                        "odorLevel",
                        "fireRiskIndex",
                        "compactionCycles", "containerWeight",
                        "supportedWasteTypes",
                        "collectionHistory",
                        "maintainerEmail"
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
                    "fillLevel",
                    "containerStatus",
                    "wasteType",
                    "temperature",
                    "lastCollection",
                    "containerConfiguration",
                    "maintenanceSchedule",
                    "collectionRouteId",
                    "batteryLevel",
                    "odorLevel",
                    "fireRiskIndex",
                    "compactionCycles", "containerWeight",
                    "supportedWasteTypes",
                    "collectionHistory",
                    "maintainerEmail"
                ]
            }
        },
        "mutable": {
            "documentation": "Subscripción del flujo historic_mutable (tipo FLOW_HISTORIC_MUTABLE) en modelo WasteContainer",
            "description": "WasteContainer:HISTORIC_MUTABLE:devices:historic_mutable",
            "status": "active",
            "subject": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "WasteContainer"
                    }
                ],
                "condition": {
                    "attrs": [
                    "TimeInstant",
                    "location",
                    "address",
                    "fillLevel",
                    "containerStatus",
                    "wasteType",
                    "temperature",
                    "lastCollection",
                    "containerConfiguration",
                    "maintenanceSchedule",
                    "collectionRouteId",
                    "batteryLevel",
                    "odorLevel",
                    "fireRiskIndex",
                    "compactionCycles","containerWeight",
                    "supportedWasteTypes",
                    "collectionHistory",
                    "maintainerEmail"
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
                    "fillLevel",
                    "containerStatus",
                    "wasteType",
                    "temperature",
                    "lastCollection",
                    "containerConfiguration",
                    "maintenanceSchedule",
                    "collectionRouteId",
                    "batteryLevel",
                    "odorLevel",
                    "fireRiskIndex",
                    "compactionCycles","containerWeight",
                    "supportedWasteTypes",
                    "collectionHistory",
                    "maintainerEmail"
                ]
            }
        },
    },
    "updateEntities":
        [
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T07:20:15.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.351782, 40.052917]}, "type": "geo:json"},
                "address": {"value": "Calle Sostenibilidad, 12. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 42.1, "type": "Number"},
                "containerStatus": {"value": "operational", "type": "Text"},
                "wasteType": {"value": "plastic", "type": "Text"},
                "temperature": {"value": 24.8, "type": "Number"},
                "lastCollection": {"value": "2024-12-29T07:45:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 800, "compactor": False, "sensors": ["fill", "tilt"], "material": "steel"},
                    "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-20", "frequency": "monthly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-PLA-03", "type": "Text"},
                "batteryLevel": {"value": 88.5, "type": "Number"},
                "odorLevel": {"value": 1.2, "type": "Number"},
                "fireRiskIndex": {"value": 0.08, "type": "Number"},
                "compactionCycles": {"value": 0, "type": "Number"},
                "containerWeight": {"value": 621.7, "type": "Number"},
                "supportedWasteTypes": {"value": ["plastic", "packaging"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-22T07:30:00Z", "2024-12-15T08:00:00Z", "2024-12-08T07:50:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "residuos@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T08:45:30.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.349021, 40.055732]}, "type": "geo:json"},
                "address": {"value": "Avenida Ecología, 3. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 91.7, "type": "Number"},
                "containerStatus": {"value": "full", "type": "Text"},
                "wasteType": {"value": "glass", "type": "Text"},
                "temperature": {"value": 22.1, "type": "Number"},
                "lastCollection": {"value": "2024-12-28T09:20:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 1500, "compactor": True, "sensors": ["fill", "temperature"],
                              "material": "recycled_metal"}, "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-10", "frequency": "weekly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-GLS-12", "type": "Text"},
                "batteryLevel": {"value": 76.3, "type": "Number"},
                "odorLevel": {"value": 0.5, "type": "Number"},
                "fireRiskIndex": {"value": 0.03, "type": "Number"},
                "compactionCycles": {"value": 215, "type": "Number"},
                "containerWeight": {"value": 1328.9, "type": "Number"},
                "supportedWasteTypes": {"value": ["glass"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-21T09:10:00Z", "2024-12-14T09:45:00Z", "2024-12-07T08:55:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "reciclaje@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T06:30:45.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.348456, 40.053289]}, "type": "geo:json"},
                "address": {"value": "Plaza Circular, 7. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 18.9, "type": "Number"},
                "containerStatus": {"value": "maintenance", "type": "Text"},
                "wasteType": {"value": "paper", "type": "Text"},
                "temperature": {"value": 26.3, "type": "Number"},
                "lastCollection": {"value": "2024-12-31T10:15:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 600, "compactor": False, "sensors": ["fill"], "material": "plastic"},
                    "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-05", "frequency": "as_needed"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-PPR-09", "type": "Text"},
                "batteryLevel": {"value": 95.8, "type": "Number"},
                "odorLevel": {"value": 0.9, "type": "Number"},
                "fireRiskIndex": {"value": 0.21, "type": "Number"},
                "compactionCycles": {"value": 0, "type": "Number"},
                "containerWeight": {"value": 387.4, "type": "Number"},
                "supportedWasteTypes": {"value": ["paper", "cardboard"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-24T10:30:00Z", "2024-12-17T11:00:00Z", "2024-12-10T10:20:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "papel@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T09:15:22.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.352114, 40.056842]}, "type": "geo:json"},
                "address": {"value": "Camino Compost, 22. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 77.5, "type": "Number"},
                "containerStatus": {"value": "operational", "type": "Text"},
                "wasteType": {"value": "organic", "type": "Text"},
                "temperature": {"value": 31.2, "type": "Number"},
                "lastCollection": {"value": "2024-12-30T06:50:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 2000, "compactor": True, "sensors": ["fill", "temperature", "gas"],
                              "material": "stainless_steel"}, "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-18", "frequency": "biweekly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-BIO-15", "type": "Text"},
                "batteryLevel": {"value": 81.7, "type": "Number"},
                "odorLevel": {"value": 4.3, "type": "Number"},
                "fireRiskIndex": {"value": 0.32, "type": "Number"},
                "compactionCycles": {"value": 342, "type": "Number"},
                "containerWeight": {"value": 1782.6, "type": "Number"},
                "supportedWasteTypes": {"value": ["organic", "green_waste"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-23T06:40:00Z", "2024-12-16T07:15:00Z", "2024-12-09T06:55:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "organico@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T10:05:18.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.347889, 40.051673]}, "type": "geo:json"},
                "address": {"value": "Bulevar Recuperación, 15. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 5.3, "type": "Number"},
                "containerStatus": {"value": "empty", "type": "Text"},
                "wasteType": {"value": "metal", "type": "Text"},
                "temperature": {"value": 19.7, "type": "Number"},
                "lastCollection": {"value": "2024-12-31T12:00:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 1000, "compactor": True, "sensors": ["fill", "weight"],
                              "material": "aluminum"}, "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-02-01", "frequency": "monthly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-MET-04", "type": "Text"},
                "batteryLevel": {"value": 99.2, "type": "Number"},
                "odorLevel": {"value": 0.2, "type": "Number"},
                "fireRiskIndex": {"value": 0.01, "type": "Number"},
                "compactionCycles": {"value": 89, "type": "Number"},
                "containerWeight": {"value": 723.1, "type": "Number"},
                "supportedWasteTypes": {"value": ["metal", "cans"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-24T12:20:00Z", "2024-12-17T11:45:00Z", "2024-12-10T12:10:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "metal@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T11:22:37.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.353297, 40.054126]}, "type": "geo:json"},
                "address": {"value": "Paseo Sostenible, 8. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 63.8, "type": "Number"},
                "containerStatus": {"value": "operational", "type": "Text"},
                "wasteType": {"value": "textile", "type": "Text"},
                "temperature": {"value": 23.5, "type": "Number"},
                "lastCollection": {"value": "2024-12-27T14:30:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 500, "compactor": False, "sensors": ["fill"], "material": "fiberglass"},
                    "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-25", "frequency": "monthly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-TXT-11", "type": "Text"},
                "batteryLevel": {"value": 85.0, "type": "Number"},
                "odorLevel": {"value": 1.8, "type": "Number"},
                "fireRiskIndex": {"value": 0.12, "type": "Number"},
                "compactionCycles": {"value": 0, "type": "Number"},
                "containerWeight": {"value": 412.6, "type": "Number"},
                "supportedWasteTypes": {"value": ["textile", "shoes"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-20T14:45:00Z", "2024-12-13T15:10:00Z", "2024-12-06T14:20:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "textil@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T12:40:55.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.350872, 40.057319]}, "type": "geo:json"},
                "address": {"value": "Glorieta Reciclado, 1. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 96.2, "type": "Number"},
                "containerStatus": {"value": "critical", "type": "Text"},
                "wasteType": {"value": "mixed", "type": "Text"},
                "temperature": {"value": 29.8, "type": "Number"},
                "lastCollection": {"value": "2024-12-26T16:00:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 1800, "compactor": True, "sensors": ["fill", "temperature", "odor"],
                              "material": "recycled_plastic"}, "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-08", "frequency": "weekly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-MIX-22", "type": "Text"},
                "batteryLevel": {"value": 67.4, "type": "Number"},
                "odorLevel": {"value": 4.9, "type": "Number"},
                "fireRiskIndex": {"value": 0.45, "type": "Number"},
                "compactionCycles": {"value": 198, "type": "Number"},
                "containerWeight": {"value": 1692.3, "type": "Number"},
                "supportedWasteTypes": {"value": ["residual", "mixed"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-19T16:20:00Z", "2024-12-12T16:50:00Z", "2024-12-05T16:10:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "residual@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T13:18:43.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.346523, 40.055001]}, "type": "geo:json"},
                "address": {"value": "Callejón Orgánico, 9. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 33.7, "type": "Number"},
                "containerStatus": {"value": "operational", "type": "Text"},
                "wasteType": {"value": "bio", "type": "Text"},
                "temperature": {"value": 27.1, "type": "Number"},
                "lastCollection": {"value": "2024-12-30T11:45:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 950, "compactor": False, "sensors": ["fill", "humidity"],
                              "material": "composite"}, "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-22", "frequency": "biweekly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-BIO-08", "type": "Text"},
                "batteryLevel": {"value": 93.6, "type": "Number"},
                "odorLevel": {"value": 3.1, "type": "Number"},
                "fireRiskIndex": {"value": 0.19, "type": "Number"},
                "compactionCycles": {"value": 0, "type": "Number"},
                "containerWeight": {"value": 698.2, "type": "Number"},
                "supportedWasteTypes": {"value": ["organic", "bio_waste"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-23T11:30:00Z", "2024-12-16T12:15:00Z", "2024-12-09T11:50:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "bio@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T14:55:29.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.354761, 40.053874]}, "type": "geo:json"},
                "address": {"value": "Travesía Limpieza, 4. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 52.4, "type": "Number"},
                "containerStatus": {"value": "needs_cleaning", "type": "Text"},
                "wasteType": {"value": "hazardous", "type": "Text"},
                "temperature": {"value": 18.3, "type": "Number"},
                "lastCollection": {"value": "2024-12-25T13:15:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 300, "compactor": False, "sensors": ["fill", "leak"],
                              "material": "chemical_resistant"}, "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-03", "frequency": "daily"}, "type": "jsonb"},
                "collectionRouteId": {"value": "RT-HAZ-19", "type": "Text"},
                "batteryLevel": {"value": 100.0, "type": "Number"},
                "odorLevel": {"value": 0.7, "type": "Number"},
                "fireRiskIndex": {"value": 0.27, "type": "Number"},
                "compactionCycles": {"value": 0, "type": "Number"},
                "containerWeight": {"value": 245.8, "type": "Number"},
                "supportedWasteTypes": {"value": ["batteries", "chemicals"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-18T13:40:00Z", "2024-12-11T14:05:00Z", "2024-12-04T13:25:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "peligrosos@ayto-argelita.es", "type": "TextUnrestricted"}
            },
            {
                "id": "ENT-WST-001",
                "type": "WasteContainer",
                "TimeInstant": {"value": "2025-01-01T15:33:14.000Z", "type": "DateTime"},
                "location": {"value": {"type": "Point", "coordinates": [-0.349635, 40.058212]}, "type": "geo:json"},
                "address": {"value": "Vereda Verde, 18. 12230 Argelita, Castellón", "type": "Text"},
                "fillLevel": {"value": 29.6, "type": "Number"},
                "containerStatus": {"value": "offline", "type": "Text"},
                "wasteType": {"value": "electronic", "type": "Text"},
                "temperature": {"value": 21.4, "type": "Number"},
                "lastCollection": {"value": "2024-12-29T17:30:00.000Z", "type": "DateTime"},
                "containerConfiguration": {
                    "value": {"capacity_kg": 400, "compactor": False, "sensors": ["fill", "tamper"],
                              "material": "anti_static"},
                    "type": "json"},
                "maintenanceSchedule": {"value": {"next_service": "2025-01-17", "frequency": "monthly"},
                                        "type": "jsonb"},
                "collectionRouteId": {"value": "RT-ELE-05", "type": "Text"},
                "batteryLevel": {"value": 45.2, "type": "Number"},
                "odorLevel": {"value": 0.3, "type": "Number"},
                "fireRiskIndex": {"value": 0.06, "type": "Number"},
                "compactionCycles": {"value": 0, "type": "Number"},
                "containerWeight": {"value": 321.9, "type": "Number"},
                "supportedWasteTypes": {"value": ["electronics", "batteries"], "type": "json"},
                "collectionHistory": {"value": ["2024-12-22T17:50:00Z", "2024-12-15T18:20:00Z", "2024-12-08T17:35:00Z"],
                                      "type": "json"},
                "maintainerEmail": {"value": "electronicos@ayto-argelita.es", "type": "TextUnrestricted"}
            }
        ]
}