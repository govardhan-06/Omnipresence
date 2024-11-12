import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:omnisecure/pages/contact.dart';
import 'package:omnisecure/pages/incident.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:omnisecure/pages/map.dart';
import 'package:omnisecure/globals.dart';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:camera/camera.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _sosPressCount = 0;
  Timer? _sosTimer;
  double lati = 0;
  double longi = 0;
  Timer? _videoTimer;
  CameraController? _cameraController;
  WebSocketChannel? _webSocketChannel;
  bool _isCapturing = false;
  int sosflag = 0;
  @override
  void initState() {
    super.initState();
    setGlobalUid();
    _requestLocationPermission();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    _cameraController =
        CameraController(cameras.first, ResolutionPreset.medium);
    await _cameraController?.initialize();
  }

  Future<void> _requestLocationPermission() async {
    PermissionStatus permission = await Permission.location.request();
    if (permission.isGranted) {
      print('Location permission granted.');
      _getCurrentLocation();
    } else if (permission.isDenied || permission.isPermanentlyDenied) {
      _showPermissionDialog();
    }
  }

  Future<void> _getCurrentLocation() async {
    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      print('Latitude: ${position.latitude}, Longitude: ${position.longitude}');
    } catch (e) {
      print('Error fetching location: $e');
    }
  }

  Future<void> _showPermissionDialog() async {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text("Location Permission Needed"),
          content: const Text(
              "To enhance safety features, this app requires location access. Please allow location permission."),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _requestLocationPermission();
              },
              child: const Text("Allow"),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                print("Permission denied by user.");
              },
              child: const Text("Deny"),
            ),
          ],
        );
      },
    );
  }

  void setGlobalUid() {
    final User? user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      uid = user.uid;
      print("Global UID set");
    } else {
      print("No user is currently logged in.");
    }
  }

  void _onSosPressed() async {
    setState(() {
      _sosPressCount++;
    });

    _sosTimer?.cancel();
    _sosTimer = Timer(const Duration(seconds: 2), () {
      _sosPressCount = 0;
    });

    if (_sosPressCount >= 3) {
      print('SOS button pressed 3 times quickly!');
      _triggerSOSAction();
      if (sosflag == 1) {
        _startVideoStream();
      }
    }
  }

  void _startVideoStream() async {
    final uri = Uri.parse("wss://$baseUrl/ws/stream/$uid/$alertid/mp4");
    _webSocketChannel = WebSocketChannel.connect(uri);
    _webSocketChannel!.stream.listen((message) {
      print("Server response: $message");
    }, onError: (error) {
      print("WebSocket error: $error");
    });

    // Store video frames in a list for 1 minute (60 seconds)
    List<Uint8List> videoFrames = [];
    final duration = Duration(minutes: 1);
    final endTime = DateTime.now().add(duration);

    // Capture frames every 200 milliseconds for 1 minute
    _videoTimer =
        Timer.periodic(const Duration(milliseconds: 200), (timer) async {
      // Check if the time limit has been reached
      if (DateTime.now().isAfter(endTime)) {
        _stopVideoStream(videoFrames); // Stop the stream after 1 minute
      } else {
        if (!_isCapturing) {
          _isCapturing = true; // Lock the capture flag

          try {
            final videoFrame = await _cameraController?.takePicture();
            final bytes = await videoFrame?.readAsBytes();

            if (bytes != null) {
              videoFrames.add(bytes); // Store each frame
            }
          } catch (e) {
            print("Error capturing picture: $e");
          } finally {
            _isCapturing =
                false; // Unlock the capture flag after capture is done
          }
        }
      }
    });
  }

  void _stopVideoStream(List<Uint8List> videoFrames) {
    _videoTimer?.cancel();
    for (var frame in videoFrames) {
      _webSocketChannel!.sink.add(frame); // Send each frame
    }
    _webSocketChannel?.sink.close();
    sosflag = 0;
    print("Video streaming stopped.");
  }

  void _triggerSOSAction() async {
    // Implement SOS action here (e.g., send an alert, message, etc.)

    print("SOS Action triggered!");
    Position position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );

    lati = position.latitude;
    longi = position.longitude;

    var sosurl = Uri.https(baseUrl, '/sos-trigger', {
      'user_id': uid,
      'latitude': lati.toString(),
      'longitude': longi.toString(),
      'username': 'meera',
    });

    final response = await http.post(
      sosurl,
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );
    if (response.statusCode == 200) {
      // The request was successful
      print('Request successful: ${response.body}');
      var sosjson = jsonDecode(response.body);
      alertid = sosjson['alert_id'];
      sosflag = 1;
    } else {
      // The request failed
      print('Request failed with status: ${response.statusCode}');
    }
    _sosPressCount = 0;
    _sosTimer?.cancel();
  }

  @override
  void dispose() {
    _sosTimer?.cancel();
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home Page'),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _onSosPressed,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color.fromARGB(255, 114, 0, 0),
                padding:
                    const EdgeInsets.symmetric(horizontal: 100, vertical: 100),
                textStyle: const TextStyle(fontSize: 24),
                elevation: 10,
                shadowColor: Colors.black.withOpacity(0.5),
              ),
              child: const Text(
                'SOS',
                style: TextStyle(color: Colors.white, fontSize: 72),
              ),
            ),
            const SizedBox(height: 40),
            Column(
              children: [
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const ReportIncidentPage()),
                    );
                    print('Report Incidents pressed!');
                  },
                  child: const Text('Report Incidents'),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => SafeMapPage()),
                    );
                    print('Safe Map Routing pressed!');
                  },
                  child: const Text('Safe Map Routing'),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const AddContactPage()),
                    );
                    print('Add Emergency Contact pressed!');
                  },
                  child: const Text('Add Emergency Contact'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
