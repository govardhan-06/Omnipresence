# Incident reportting using GraphQL

To be used for setting up the anonymous incident reporting feature. GraphQL is basically a query based language for APIs. The reports will be stored and fetched from supabase which is built on PostgreSQL.

## Backend

If you're using Supabase as your database, integrating it with FastAPI and GraphQL is straightforward. Supabase is built on PostgreSQL, and it provides a RESTful API by default, but you can also interact with it using direct database queries in FastAPI. Here's how you can set up your FastAPI application to work with Supabase while utilizing GraphQL.

### Step-by-Step Integration of FastAPI with Supabase and GraphQL

#### 1. **Set Up Your Supabase Project**

1. Go to [Supabase](https://supabase.com/) and create a new project.
2. Configure your database tables according to your application's needs (e.g., a `reports` table).
3. Get the connection string for your Supabase database from the project settings.

#### 2. **Install Required Libraries**

Make sure you have the following libraries installed:

```bash
pip install fastapi uvicorn psycopg2-binary sqlalchemy graphene fastapi-graphql asyncpg supabase
```

- `psycopg2-binary`: PostgreSQL adapter for Python.
- `asyncpg`: For asynchronous database access with PostgreSQL.
- `supabase`: To interact with Supabase's API.

#### 3. **Set Up FastAPI with GraphQL**

Here's a basic setup to get you started:

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_graphql import GraphQLApp
import graphene
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client, Client
import os
from datetime import datetime

# Initialize FastAPI
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DATABASE_URL = os.getenv("SUPABASE_DB_URL")  # Set this environment variable
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client: Client = create_client(supabase_url, supabase_key)

# SQLAlchemy Models
Base = declarative_base()

class ReportModel(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(String)
    report_type = Column(String)
    timestamp = Column(DateTime)

# GraphQL Schema
class Report(graphene.ObjectType):
    id = graphene.Int()
    location = graphene.String()
    latitude = graphene.Float()
    longitude = graphene.Float()
    description = graphene.String()
    report_type = graphene.String()
    timestamp = graphene.DateTime()

class CreateReport(graphene.Mutation):
    class Arguments:
        location = graphene.String(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)
        description = graphene.String(required=True)
        report_type = graphene.String(required=True)

    report = graphene.Field(Report)

    async def mutate(self, info, location, latitude, longitude, description, report_type):
        # Insert into Supabase
        data = {
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
            "report_type": report_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = supabase_client.table("reports").insert(data).execute()
        new_report = response.data[0] if response.data else None

        if not new_report:
            raise Exception("Failed to create report")

        return CreateReport(report=new_report)

class Query(graphene.ObjectType):
    reports = graphene.List(Report)

    async def resolve_reports(self, info):
        # Fetch reports from Supabase
        response = supabase_client.table("reports").select("*").execute()
        reports = response.data

        return [Report(**report) for report in reports] if reports else []

class Mutation(graphene.ObjectType):
    create_report = CreateReport.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# Add GraphQL route
app.add_route("/graphql", GraphQLApp(schema=schema))
```

### 4. **Set Environment Variables**

Make sure to set your Supabase URL and API key as environment variables:

```bash
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### 5. **Run Your FastAPI Application**

Run your FastAPI application with Uvicorn:

```bash
uvicorn main:app --reload
```

Replace `main` with the name of your Python file if it's different.

### 6. **Access the GraphQL API**

Open your browser and navigate to `http://127.0.0.1:8000/graphql`. You can use this interface to run queries and mutations directly.

### Example GraphQL Queries

1. **Create a Report (Mutation)**:

```graphql
mutation {
  createReport(
    location: "Central Park"
    latitude: 40.785091
    longitude: -73.968285
    description: "Suspicious activity near the playground."
    reportType: "Suspicious Activity"
  ) {
    report {
      id
      location
      description
    }
  }
}
```

2. **Fetch Reports (Query)**:

```graphql
query {
  reports {
    id
    location
    description
    timestamp
  }
}
```

### Conclusion

With this setup, you now have a FastAPI application that integrates with Supabase for database operations and provides a GraphQL API to interact with user-reported safety incidents. You can further enhance your application by implementing more complex queries, error handling, and authentication as needed. If you have any specific questions or need further assistance, feel free to ask!

## Flutter App integration

To enable your Flutter app to access the FastAPI GraphQL API for reporting and fetching data, you can follow these steps. This involves making HTTP requests from your Flutter app to the GraphQL endpoint you've set up. Below is a comprehensive guide on how to implement this.

### Step 1: Setup Flutter Project

If you haven't already, create a new Flutter project:

```bash
flutter create safety_app
cd safety_app
```

### Step 2: Add Dependencies

Add the required dependencies for making HTTP requests and for handling GraphQL in your `pubspec.yaml` file:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^0.14.0
  graphql_flutter: ^5.0.0
```

Then, run:

```bash
flutter pub get
```

### Step 3: Configure GraphQL Client

Set up the GraphQL client in your Flutter app. This is typically done in the `main.dart` file or a separate service file. Here’s how to do it in `main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:graphql_flutter/graphql_flutter.dart';

void main() async {
  await initHiveForFlutter();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final HttpLink httpLink = HttpLink('http://127.0.0.1:8000/graphql');

    final GraphQLClient client = GraphQLClient(
      link: httpLink,
      cache: GraphQLCache(store: HiveStore()),
    );

    return GraphQLProvider(
      client: client,
      child: MaterialApp(
        title: 'Safety App',
        home: HomeScreen(),
      ),
    );
  }
}
```

Make sure to replace the `httpLink` with your FastAPI URL. If you're testing on a device or emulator, ensure that the IP address is accessible.

### Step 4: Implement Reporting Functionality

Create a function in your Flutter app to send a report to the FastAPI server. This will use a mutation to create a new report. Here’s an example of how to implement this:

```dart
class HomeScreen extends StatelessWidget {
  final String createReportMutation = """
    mutation CreateReport(\$location: String!, \$latitude: Float!, \$longitude: Float!, \$description: String!, \$reportType: String!) {
      createReport(location: \$location, latitude: \$latitude, longitude: \$longitude, description: \$description, reportType: \$reportType) {
        report {
          id
          location
          description
          timestamp
        }
      }
    }
  """;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Safety App'),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            _reportIncident(context);
          },
          child: Text('Report Incident'),
        ),
      ),
    );
  }

  void _reportIncident(BuildContext context) {
    final variables = {
      "location": "Central Park",
      "latitude": 40.785091,
      "longitude": -73.968285,
      "description": "Suspicious activity near the playground.",
      "reportType": "Suspicious Activity"
    };

    final GraphQLClient client = GraphQLProvider.of(context).client;

    client.mutate(MutationOptions(
      document: gql(createReportMutation),
      variables: variables,
    )).then((result) {
      if (result.hasException) {
        print("Error: ${result.exception.toString()}");
      } else {
        print("Report created: ${result.data['createReport']['report']}");
      }
    });
  }
}
```

### Step 5: Implement Fetching Reports

To fetch reports from your FastAPI server, create a query and use it in a similar manner:

```dart
class ReportsScreen extends StatelessWidget {
  final String fetchReportsQuery = """
    query {
      reports {
        id
        location
        description
        timestamp
      }
    }
  """;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reports'),
      ),
      body: Query(
        options: QueryOptions(
          document: gql(fetchReportsQuery),
          pollInterval: Duration(seconds: 10), // Optional: auto-refresh every 10 seconds
        ),
        builder: (QueryResult result, { VoidCallback? refetch, FetchMore? fetchMore }) {
          if (result.isLoading) {
            return Center(child: CircularProgressIndicator());
          }

          if (result.hasException) {
            return Center(child: Text("Error: ${result.exception.toString()}"));
          }

          final reports = result.data!['reports'] as List;

          return ListView.builder(
            itemCount: reports.length,
            itemBuilder: (context, index) {
              final report = reports[index];
              return ListTile(
                title: Text(report['location']),
                subtitle: Text(report['description']),
                trailing: Text(report['timestamp']),
              );
            },
          );
        },
      ),
    );
  }
}
```

### Step 6: Navigation and Testing

You can navigate between screens using Flutter's navigation methods, such as:

```dart
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => ReportsScreen()),
);
```

### Step 7: Test the Application

- Run your FastAPI server.
- Make sure your Flutter app is configured correctly with the FastAPI URL.
- Use an emulator or physical device to test the reporting and fetching functionality.

### Conclusion

With these steps, your Flutter application should be able to report incidents and fetch reports from your FastAPI backend via GraphQL. You can enhance the user interface and add more features like form inputs, error handling, and data validation as needed. If you have any specific questions or need further assistance, feel free to ask!
