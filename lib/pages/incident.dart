import 'package:flutter/material.dart';
import 'package:omnisecure/globals.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ReportIncidentPage extends StatefulWidget {
  const ReportIncidentPage({super.key});

  @override
  _ReportIncidentPageState createState() => _ReportIncidentPageState();
}

class _ReportIncidentPageState extends State<ReportIncidentPage> {
  // Form controllers and variables
  final TextEditingController locationController = TextEditingController();
  final TextEditingController timeController = TextEditingController();
  final TextEditingController descriptionController = TextEditingController();
  final TextEditingController urgencyController = TextEditingController();
  final TextEditingController witnessesController = TextEditingController();
  final TextEditingController commentsController = TextEditingController();
  final TextEditingController reporterController =
      TextEditingController(text: 'anonymous');

  String selectedIncidentType = 'Harassment';
  final List<String> incidentTypes = [
    'Harassment',
    'Suspicious Activity',
    'Theft and Vandalism',
    'Physical Assault',
    'Emergency Situation',
    'Unsafe Condition',
    'Public Misconduct',
    'Gender-Based Violence',
    'Safety Concern',
    'Others',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Report Incident'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Incident Type Dropdown
              const Text('Incident Type'),
              DropdownButtonFormField<String>(
                value: selectedIncidentType,
                items: incidentTypes.map((type) {
                  return DropdownMenuItem(
                    value: type,
                    child: Text(type),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    selectedIncidentType = value!;
                  });
                },
                decoration: const InputDecoration(border: OutlineInputBorder()),
              ),
              const SizedBox(height: 16.0),

              // Location Input
              const Text('Location'),
              TextField(
                controller: locationController,
                decoration: const InputDecoration(
                  hintText: 'Enter location',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16.0),

              // Time of Incident Input
              const Text('Time of Incident'),
              TextField(
                controller: timeController,
                decoration: const InputDecoration(
                  hintText: 'Enter time of incident',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16.0),

              // Description Input
              const Text('Description'),
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(
                  hintText: 'Describe the incident',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16.0),

              // Urgency Level Input
              const Text('Urgency Level'),
              TextField(
                controller: urgencyController,
                decoration: const InputDecoration(
                  hintText: 'Enter urgency level',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16.0),

              // Witnesses Input
              const Text('Witnesses'),
              TextField(
                controller: witnessesController,
                decoration: const InputDecoration(
                  hintText: 'Enter witnesses',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16.0),

              // Additional Comments Input
              const Text('Additional Comments'),
              TextField(
                controller: commentsController,
                decoration: const InputDecoration(
                  hintText: 'Any additional comments',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16.0),

              // Reported By (Default: anonymous)
              const Text('Reported By'),
              TextField(
                controller: reporterController,
                readOnly: true,
                decoration: const InputDecoration(
                  hintText: 'anonymous',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24.0),

              // Submit Button
              Center(
                child: ElevatedButton(
                  onPressed: () async {
                    var incidenturl = Uri.http(baseUrl, '/report-incident', {
                      'uid': uid,
                    });
                    var incidentData = {
                      'incident_type': selectedIncidentType,
                      'location': locationController.text,
                      'time_of_incident': timeController.text,
                      'description': descriptionController.text,
                      'urgency_level': urgencyController.text,
                      'witnesses': witnessesController.text,
                      'additional_comments': commentsController.text,
                      'reported_by': reporterController.text,
                    };
                    final response = await http.post(
                      incidenturl,
                      headers: <String, String>{
                        'Content-Type': 'application/json; charset=UTF-8',
                      },
                      body: jsonEncode(incidentData),
                    );
                    if (response.statusCode == 200) {
                      // The request was successful
                      print('Request successful: ${response.body}');
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content:
                              const Text('Incident reported successfully!'),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                              'Failed to report incident. Status code: ${response.statusCode}'),
                          backgroundColor: Colors.red,
                        ),
                      );
                      // The request failed
                      print(
                          'Request failed with status: ${response.statusCode}');
                    }

                    // Handle form submission

                    print('Incident Reported: $incidentData');
                    locationController.clear();
                    timeController.clear();
                    descriptionController.clear();
                    urgencyController.clear();
                    witnessesController.clear();
                    commentsController.clear();
                    reporterController.clear();

                    // Add functionality to submit or save the report data
                  },
                  child: const Text('Submit Report'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    // Dispose controllers when not needed
    locationController.dispose();
    timeController.dispose();
    descriptionController.dispose();
    urgencyController.dispose();
    witnessesController.dispose();
    commentsController.dispose();
    reporterController.dispose();
    super.dispose();
  }
}
