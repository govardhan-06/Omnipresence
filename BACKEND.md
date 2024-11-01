# Omnipresence Backend API Documentation

This API documentation describes endpoints for the **Omnipresence Project**, a women's safety and empowerment system leveraging AI for real-time analysis and geolocation-based alerting. This FastAPI-based backend is containerized in Docker, making it deployable across various environments.

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

- **Endpoint**: `POST /add-geofence`
- **Parameters**:
  - `geofence` (Geofence): Geofence details including location and radius.
- **Description**: Admin-only endpoint to create geofences for incident areas.
- **Response**:
  - **200**: Geofence added successfully.
  - **400**: Failed to add geofence.
  - **500**: Validation error.

#### 9. **Get All Geofence Coordinates**

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
