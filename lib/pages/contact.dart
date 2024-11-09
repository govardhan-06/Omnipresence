import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:omnisecure/globals.dart';

class AddContactPage extends StatefulWidget {
  const AddContactPage({super.key});

  @override
  _AddContactPageState createState() => _AddContactPageState();
}

class _AddContactPageState extends State<AddContactPage> {
  final TextEditingController nameController = TextEditingController();
  final TextEditingController relationController = TextEditingController();
  final TextEditingController phoneNumberController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Emergency Contact'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Name Input
            const Text('Name'),
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                hintText: 'Enter name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16.0),

            // Relation Input
            const Text('Relation'),
            TextField(
              controller: relationController,
              decoration: const InputDecoration(
                hintText: 'Enter relation (e.g., Friend, Parent)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16.0),

            // Phone Number Input
            const Text('Phone Number'),
            TextField(
              controller: phoneNumberController,
              decoration: const InputDecoration(
                hintText: 'Enter phone number',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 24.0),

            // Submit Button
            Center(
              child: ElevatedButton(
                onPressed: () async {
                  var incidenturl = Uri.http(baseUrl, '/family_details', {
                    'user_id': uid,
                  });

                  // Collect contact data
                  var contactData = [
                    {
                      "name": nameController.text,
                      "relation": relationController.text,
                      "phone_number": phoneNumberController.text,
                    }
                  ];
                  final response = await http.post(
                    incidenturl,
                    headers: <String, String>{
                      'Content-Type': 'application/json; charset=UTF-8',
                    },
                    body: jsonEncode(contactData),
                  );

                  if (response.statusCode == 200) {
                    // The request was successful
                    print('Request successful: ${response.body}');
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: const Text('Contact added successfully!'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                            'Failed to add contact. Status code: ${response.statusCode}'),
                        backgroundColor: Colors.red,
                      ),
                    );
                    // The request failed
                    print('Request failed with status: ${response.statusCode}');
                  }

                  // Show success SnackBar

                  // Clear text fields after submission
                  nameController.clear();
                  relationController.clear();
                  phoneNumberController.clear();

                  // Print contact data (replace with actual submission logic)
                },
                child: const Text('Submit Contact'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    nameController.dispose();
    relationController.dispose();
    phoneNumberController.dispose();
    super.dispose();
  }
}
