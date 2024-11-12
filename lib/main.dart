import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:omnisecure/globals.dart';
import 'package:omnisecure/pages/HomePage.dart';
import 'package:omnisecure/pages/login.dart';
import 'package:workmanager/workmanager.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:permission_handler/permission_handler.dart'; // Import permission handler

void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    try {
      // Get the current user
      User? user = FirebaseAuth.instance.currentUser;
      if (user != null) {
        // Fetch current location
        Position position = await Geolocator.getCurrentPosition();

        // Prepare request body
        final body = jsonEncode({
          "user_id": user.uid,
          "latitude": position.latitude,
          "longitude": position.longitude,
        });
        var locationurl = Uri.http(baseUrl, '/update_location');

        final response = await http.post(
          locationurl,
          headers: <String, String>{
            'Content-Type': 'application/json; charset=UTF-8',
          },
          body: jsonEncode(body),
        );

        if (response.statusCode == 200) {
          print("Location updated successfully.");
        } else {
          print("Failed to update location: ${response.statusCode}");
        }
      }
    } catch (e) {
      print("Error in background task: $e");
    }
    return Future.value(true);
  });
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  // Request camera permission before app loads
  await _requestPermissions();

  Workmanager().initialize(callbackDispatcher);
  // Register background task for location updates every 3 minutes
  Workmanager().registerPeriodicTask(
    'locationUpdateTask',
    'postLocation',
    frequency: Duration(minutes: 3),
  );

  runApp(const MainApp());
}

// Function to request camera and location permissions
Future<void> _requestPermissions() async {
  // Request camera permission
  PermissionStatus cameraPermission = await Permission.camera.request();
  if (cameraPermission.isGranted) {
    print('Camera permission granted.');
  } else {
    print('Camera permission denied or permanently denied.');
    // Handle denial: show a dialog or redirect to settings
  }

  // Request location permission as well
  PermissionStatus locationPermission = await Permission.location.request();
  if (locationPermission.isGranted) {
    print('Location permission granted.');
  } else {
    print('Location permission denied or permanently denied.');
    // Handle denial
  }
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: const AuthCheck(), // AuthCheck decides if the user should go to HomePage or LoginPage
    );
  }
}

class AuthCheck extends StatefulWidget {
  const AuthCheck({super.key});

  @override
  _AuthCheckState createState() => _AuthCheckState();
}

class _AuthCheckState extends State<AuthCheck> {
  User? _user;

  @override
  void initState() {
    super.initState();
    _checkUserStatus();
  }

  Future<void> _checkUserStatus() async {
    // Check if there is a currently logged-in user
    setState(() {
      _user = FirebaseAuth.instance.currentUser;
    });
  }

  @override
  Widget build(BuildContext context) {
    // If a user is logged in, navigate to HomePage; otherwise, go to LoginPage
    if (_user != null) {
      return const HomePage();
    } else {
      return LoginPage();
    }
  }
}
