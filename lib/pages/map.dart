import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart'; // Required for FlutterMap
import 'package:latlong2/latlong.dart'; // For LatLng type
import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:omnisecure/globals.dart';

class SafeMapPage extends StatefulWidget {
  const SafeMapPage({Key? key}) : super(key: key);

  @override
  _SafeMapPageState createState() => _SafeMapPageState();
}

class _SafeMapPageState extends State<SafeMapPage> {
  MapController _mapController = MapController();
  List<LatLng> routeCoordinates = [];
  bool isLoading = false; // Initially set to false

  final TextEditingController _startController = TextEditingController();
  final TextEditingController _endController = TextEditingController();

  Future<void> _fetchRoute() async {
    String startpt = _startController.text;
    String endpt = _endController.text;

    var mapurl = Uri.http(baseUrl, '/safe_route', {
      'start': startpt,
      'end': endpt,
    });

    setState(() {
      isLoading = true; // Set loading to true when the request is initiated
    });

    final response = await http.post(
      mapurl,
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final route = data['safe_route'] as List<dynamic>;

      setState(() {
        routeCoordinates = route
            .map((point) => LatLng(point[1] as double, point[0] as double))
            .toList();
        isLoading = false; // Set loading to false after the response
      });

      // After the route is fetched, adjust the map view
      _adjustMapView();
    } else {
      setState(() {
        isLoading = false; // Set loading to false if the request fails
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to fetch route')),
      );
    }
  }

  // Function to adjust the map view based on the route's coordinates
  void _adjustMapView() {
    if (routeCoordinates.isNotEmpty) {
      double minLat = routeCoordinates.first.latitude;
      double maxLat = routeCoordinates.first.latitude;
      double minLng = routeCoordinates.first.longitude;
      double maxLng = routeCoordinates.first.longitude;

      // Find the min/max latitudes and longitudes
      for (var point in routeCoordinates) {
        if (point.latitude < minLat) minLat = point.latitude;
        if (point.latitude > maxLat) maxLat = point.latitude;
        if (point.longitude < minLng) minLng = point.longitude;
        if (point.longitude > maxLng) maxLng = point.longitude;
      }

      // Calculate the center of the route
      LatLng center = LatLng((minLat + maxLat) / 2, (minLng + maxLng) / 2);
      double zoomLevel = 14.0;

      // Adjust the map's center and zoom
      _mapController.move(center, zoomLevel);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Safe Map Routing'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Text fields for start and end points
                TextField(
                  controller: _startController,
                  decoration: InputDecoration(
                    labelText: 'Start Point',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _endController,
                  decoration: InputDecoration(
                    labelText: 'End Point',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                // Button to fetch the route
                ElevatedButton(
                  onPressed: _fetchRoute,
                  child: const Text('Show Route'),
                ),
              ],
            ),
          ),
          // Check if loading is true, then show loading indicator
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : Expanded(
                  child: FlutterMap(
                    mapController: _mapController,
                    options: MapOptions(
                        // center: routeCoordinates.isNotEmpty
                        //     ? routeCoordinates.first
                        //     : LatLng(0, 0),
                        // zoom: 14.0,
                        ),
                    children: [
                      TileLayer(
                        urlTemplate:
                            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        subdomains: ['a', 'b', 'c'],
                      ),
                      PolylineLayer(
                        polylines: [
                          Polyline(
                            points: routeCoordinates,
                            strokeWidth: 4.0,
                            color: Colors.blue,
                          ),
                        ],
                      ),
                      // Adding circles for start and end points
                      if (routeCoordinates.isNotEmpty) ...[
                        CircleLayer(
                          circles: [
                            CircleMarker(
                              point: routeCoordinates.first,
                              color: Color.fromARGB(255, 74, 46, 255)
                                  .withOpacity(0.7),
                              radius: 12.0,
                            ),
                            CircleMarker(
                              point: routeCoordinates.last,
                              color: Color.fromARGB(255, 47, 255, 0)
                                  .withOpacity(0.7),
                              radius: 18.0,
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
        ],
      ),
    );
  }
}
