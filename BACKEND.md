# Omnipresence Backend API Documentation

This API documentation describes endpoints for the **Omnipresence Project**, a women's safety and empowerment system leveraging AI for real-time analysis and geolocation-based alerting. This FastAPI-based backend is containerized in Docker, making it deployable across various environments.

---

## Docker Image Setup

This section provides instructions for setting up the Docker environment for the `govardhan06/omnipresence-backend` image. Follow these steps to create a network, pull the necessary images, and run the containers.

### Step 1: Create Docker Network

First, create a Docker network that will allow your containers to communicate with each other:

```bash
docker network create omnipresence-network
```

### Step 2: Pull and Run the Omnipresence Backend Image

Next, pull the Omnipresence backend image and run it within the created network:

```bash
docker pull govardhan06/omnipresence-backend:v1
docker run --name omnipresence-backend --network omnipresence-network govardhan06/omnipresence-backend:v1
```

### Step 3: Pull and Run the IPFS Node

Now, you will need to set up an IPFS node for handling anonymous incident reporting. Pull the latest IPFS image and run it in the same network:

```bash
docker run -d --name ipfs-node --network omnipresence-network -v ipfs_data:/data/ipfs -e IPFS_PROFILE=server ipfs/go-ipfs:latest
```

### Verification

To verify that both containers are running correctly within the `omnipresence-network`, you can use the following command:

```bash
docker ps
```

This will display a list of running containers, including the `omniverse-backend` and `ipfs-node`.

### Notes

- Ensure Docker is installed and running on your machine before executing these commands.
- The endpoints must be triggered only after setting-up both of these images

---

## Features
- `govardhan06/omnipresence-backend:v1`

### 1. Anonymous Incident Reporting with IPFS Integration
Users can report incidents anonymously through the backend, ensuring privacy and security. Reports are stored using IPFS (InterPlanetary File System), providing a decentralized and secure way to handle sensitive data without compromising user identity.

### 2. Point-to-Point Safe Routing
The backend facilitates safe routing by calculating and suggesting the safest paths based on real-time data. Users can input their destination, and the system will provide optimized routes that avoid high-risk areas, ensuring a safer travel experience.

### 3. Emergency Contact Setup
Users can configure emergency contacts within the application. In case of an emergency, the system can quickly notify these contacts, ensuring rapid communication and support during critical situations.

### 4. WhatsApp API Integration
The backend integrates with the WhatsApp API, allowing users to send alerts and notifications directly to their contacts via WhatsApp. This feature ensures timely communication in emergencies, leveraging a widely used messaging platform.

### 5. SOS Trigger and Corresponding Chain of Events
Users can activate an SOS trigger with a simple action. Upon activation, a predefined chain of events is initiated, including notifications to emergency contacts, location sharing, and alerting local authorities if necessary, ensuring immediate assistance.

### 6. Streaming of Video from Phone on SOS Trigger
In case of an SOS trigger, users can stream live video from their phone's camera to the backend. This feature provides real-time visual information to emergency contacts and responders, enhancing situational awareness and response effectiveness.

---

### Endpoints

#### 1. **Home Redirect**

- **Endpoint**: `GET /`
- **Description**: Redirects users to the API documentation (Swagger UI).
- **Response**:
  - **200**: Redirect to `/docs`.

#### 2. **User Login or Registration**

- **Endpoint**: `POST /login-or-register`
- **Parameters**:
  - `token` (str): Firebase ID Token for authentication.
- **Description**: Authenticates or registers users using Firebase. If the user is new, creates a record in Supabase.
- **Response**:
  - **200**: User verified or created.
  - **401**: Invalid token.
  - **500**: Internal Server Error.

#### 3. **Add Family Details**

- **Endpoint**: `POST /family_details`
- **Parameters**:
  - `user_id` (str): User identifier.
  - `family_members` (List[FamilyMember]): List of family members' details.
- **Description**: Stores family contact details in IPFS and records the hash in Supabase for emergency use.
- **Response**:
  - **200**: Family details added.
  - **500**: Failed to store data in Supabase or IPFS.

#### 4. **Get Family Details**

- **ADMIN ACCESS**
- **Endpoint**: `GET /family_details/{user_id}`
- **Parameters**:
  - `user_id` (str): User identifier.
- **Description**: Retrieves family contact details from IPFS using Supabase.
- **Response**:
  - **200**: Data successfully retrieved.
  - **500**: Failed to retrieve data.

#### 5. **Report Incident**

- **Endpoint**: `POST /report-incident`
- **Parameters**:
  - `uid` (str): User identifier.
  - `incident` (Incident): Incident details including type, location, and time.
- **Description**: Crowdsources incident reports and stores details in IPFS. A geofence is set up around the incident.
- **Response**:
  - **200**: Incident recorded, hash saved in Supabase.
  - **500**: Failed to store data in IPFS or Supabase.

#### 6. **Retrieve Incidents**

- **ADMIN ACCESS**
- **Endpoint**: `GET /retrieve-incident`
- **Description**: Admin-only endpoint to fetch all incident reports.
- **Response**:
  - **200**: Incident data retrieved from IPFS.
  - **500**: Failed to retrieve incident data.

#### 7. **Update User Location**

- **Endpoint**: `POST /update_location`
- **Parameters**:
  - `location` (UserLocation): User's current latitude and longitude.
- **Description**: Updates user location and checks if the user is within any defined geofence. Sends an alert if necessary.
- **Response**:
  - **200**: Geofence alerts if applicable.
  - **500**: Failed to update location.

#### 8. **Add Geofence**

- **ADMIN ACCESS**
- **Endpoint**: `POST /add-geofence`
- **Parameters**:
  - `geofence` (Geofence): Geofence details including location and radius.
- **Description**: Admin-only endpoint to create geofences for incident areas.
- **Response**:
  - **200**: Geofence added successfully.
  - **400**: Failed to add geofence.
  - **500**: Validation error.

#### 9. **Get All Geofence Coordinates**

- **ADMIN ACCESS**
- **Endpoint**: `GET /geofence_coordinates`
- **Description**: Admin-only endpoint to retrieve all geofence data.
- **Response**:
  - **200**: Geofence coordinates retrieved.
  - **500**: Failed to retrieve geofences.

#### 10. **Get Safe Route**

- **Endpoint**: `GET /safe_route`
- **Parameters**:
  - `start_lat` (float): Starting latitude.
  - `start_lon` (float): Starting longitude.
  - `end_lat` (float): Destination latitude.
  - `end_lon` (float): Destination longitude.
- **Description**: Calculates the safest route between two points, avoiding areas within active geofences.
- **Response**:
  - **200**: Route data.
  - **404**: Route not found.

#### 11. **Trigger SOS Alert**

- **Endpoint**: `POST /sos-trigger`
- **Parameters**:
  - `user_id` (str): User identifier.
  - `latitude` (float): Current latitude.
  - `longitude` (float): Current longitude.
  - `username` (str): User's name.
- **Description**: Sends an SOS alert, notifying emergency contacts of the user's location.
- **Response**:
  - **200**: SOS alert triggered, alert ID returned.

#### 12. **Retrieve SOS Alert Data**

- **Endpoint**: `GET /sos-alert/{user_id}/{alert_id}`
- **Parameters**:
  - `user_id` (str): User identifier.
  - `alert_id` (int): SOS alert identifier.
- **Description**: Admin-only endpoint to retrieve specific SOS alert data.
- **Response**:
  - **200**: SOS data retrieved.
  - **404**: Alert not found.

#### 13. **Live Stream SOS Alert**

- **Endpoint**: `WebSocket /ws/stream/{user_id}/{alert_id}`
- **Parameters**:
  - `user_id` (str): User identifier.
  - `alert_id` (int): SOS alert identifier.
- **Description**: WebSocket for real-time media streaming related to an SOS alert.
- **Response**:
  - Real-time stream initiated on connection.
